"""CLI principal do kb."""

import typer
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table

app = typer.Typer(
    help="LLM-powered personal knowledge base",
    epilog=(
        "Opções por comando:\n\n"
        "ingest <src...>  [--no-commit|--commit] [--compile]\n\n"
        "import-book <arquivo...>  [--output PATH] [--compile] [--force] [--ocr]"
        "  [--workers/-j INT] [--chunk-pages INT] [--allow-sensitive] [--no-commit|--commit]\n\n"
        "compile (alvo)  [--workers/-j INT] [--allow-sensitive] [--no-commit|--commit]"
        "  [--no-update-index]\n\n"
        "qa <pergunta>  [--file-back/-f] [--to-wiki] [--depth INT] [--no-traverse]"
        "  [--allow-sensitive] [--no-commit|--commit]\n\n"
        "search <query>\n\n"
        "lint  [--allow-sensitive]\n\n"
        "heal  [--n/-n INT] [--allow-sensitive] [--no-commit|--commit]\n\n"
        "jobs list  |  jobs run <nome>  |  jobs gate  |  jobs cron  |  jobs doc-gate\n\n"
        "discovery run  [--query TEXTO] [--max-per-source INT] [--compile/--no-compile]"
        " [--allow-sensitive] [--no-commit|--commit]\n\n"
        "handoff create --scope <texto> [--summary] [--next-steps] [--evidence] [--decisions]"
    ),
)
jobs_app = typer.Typer(help="Jobs canônicos e agendáveis do kb")
discovery_app = typer.Typer(help="Descoberta automatizada e ingestão periódica")
handoff_app = typer.Typer(help="Handoff operacional de sessão")
app.add_typer(jobs_app, name="jobs")
app.add_typer(discovery_app, name="discovery")
app.add_typer(handoff_app, name="handoff")
console = Console()


@app.command()
def ingest(
    sources: list[str] = typer.Argument(
        ..., help="Arquivo(s) ou URL(s) para adicionar a raw/"
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão: escreve localmente sem commit; use --commit para versionar",
    ),
    compile_after: bool = typer.Option(
        False,
        "--compile",
        help="Compila os arquivos ingeridos para wiki/ após ingestão",
    ),
):
    """Copia arquivo(s) para raw/ ou raspa URL(s) e salva como Markdown."""
    from kb.config import RAW_DIR
    from kb.state import record_ingest

    ingested: list[Path] = []

    for source in sources:
        if source.startswith("http://") or source.startswith("https://"):
            from kb.web_ingest import WebIngestError, ingest_url

            console.print(f"[dim]Baixando {source}...[/]")
            try:
                out = ingest_url(source, no_commit=no_commit)
            except WebIngestError as exc:
                console.print(f"[red]Erro:[/] {exc}")
                raise typer.Exit(code=1)
            record_ingest(out)
            console.print(f"[green]Adicionado:[/] {out}")
            ingested.append(out)
        else:
            path = Path(source)
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            dest = RAW_DIR / path.name
            dest.write_bytes(path.read_bytes())
            record_ingest(dest)
            if not no_commit:
                from kb.git import commit

                commit(f"feat(raw): ingest — {path.name}", [dest])
            console.print(f"[green]Adicionado:[/] {dest}")
            ingested.append(dest)

    if compile_after and ingested:
        from kb.compile import compile_file, update_index as do_update_index

        for f in ingested:
            console.print(f"Compilando [bold]{f.name}[/]...")
            out = compile_file(f, no_commit=no_commit)
            rel = out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out
            console.print(f"  → [green]{rel}[/]")
        do_update_index(no_commit=no_commit)


@app.command("import-book")
def import_book(
    paths: List[Path] = typer.Argument(
        ..., help="Arquivo(s) EPUB ou PDF textual para importar em capítulos Markdown"
    ),
    output: Path = typer.Option(
        None,
        "--output",
        help="Diretório de saída (padrão: raw/books/<livro>); ignorado se múltiplos arquivos",
    ),
    compile_imported: bool = typer.Option(
        False,
        "--compile",
        help="Compilar os capítulos importados para wiki/ após a importação",
    ),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão: escreve localmente sem commit; use --commit para versionar",
    ),
    ocr: bool = typer.Option(
        False,
        "--ocr",
        help="Usar OCR para PDFs de scan ou com encoding de fonte inválido (requer kb[ocr])",
    ),
    force: bool = typer.Option(
        False, "--force", help="Reimportar livros já existentes em raw/books/"
    ),
    workers: int = typer.Option(
        4, "--workers", "-j", help="Número de livros processados em paralelo"
    ),
    chunk_pages: int = typer.Option(
        15, "--chunk-pages", help="Páginas por chunk no fallback (PDFs sem TOC)"
    ),
):
    """Importa um ou mais livros EPUB ou PDF textual para raw/books/ em arquivos Markdown por capítulo."""
    from kb.book_import import BookImportError, default_output_dir, import_epub
    from kb.git import commit

    all_written: List[Path] = []
    all_imported: List[Path] = []
    results_map = {}  # path → (status, detail) para manter ordem original na tabela

    def _process(path: Path):
        target_dir = (output if len(paths) == 1 else None) or default_output_dir(path)
        if not force and target_dir.exists() and any(target_dir.glob("*.md")):
            return path, "skip", target_dir
        try:
            written_files, metadata_path = import_epub(
                path, target_dir, use_ocr=ocr, chunk_pages=chunk_pages
            )
            return path, "ok", (written_files, metadata_path)
        except (BookImportError, PermissionError) as exc:
            return path, "fail", str(exc)
        except Exception as exc:
            detail = str(exc) or type(exc).__name__
            return path, "fail", f"Erro inesperado ({type(exc).__name__}): {detail}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Importando livros...[/] {task.completed}/{task.total}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("", total=len(paths))

        with ThreadPoolExecutor(max_workers=min(workers, len(paths))) as executor:
            futures = {executor.submit(_process, path): path for path in paths}
            for future in as_completed(futures):
                path, status, detail = future.result()
                results_map[path] = (status, detail)
                progress.advance(task)

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Status", width=8)
    table.add_column("Livro")
    table.add_column("Detalhe", justify="right")

    for path in paths:
        status, detail = results_map[path]
        label = path.name[:60] + "..." if len(path.name) > 60 else path.name
        if status == "ok":
            written_files, metadata_path = detail
            all_written.extend(written_files)
            all_imported.extend([*written_files, metadata_path])
            output_dir = metadata_path.parent
            detail_label = f"[dim]{len(written_files)} capítulos[/]"
            if output_dir is not None:
                detail_label = f"{detail_label} [dim]{output_dir}[/]"
            table.add_row("[green]OK[/]", label, detail_label)
        elif status == "skip":
            table.add_row("[dim]PULADO[/]", label, "[dim]já importado[/]")
        else:
            table.add_row("[bold red]FALHOU[/]", label, f"[red]{detail}[/]")

    console.print()
    console.print(table)

    if len(paths) == 1:
        status, detail = results_map[paths[0]]
        if status == "ok" and detail:
            typer.echo(str(detail[1].parent))
        elif status == "skip":
            typer.echo(str(detail))

    failed = [p for p in paths if results_map[p][0] == "fail"]
    if failed:
        console.print(f"\n[bold red]FALHAS: {len(failed)}/{len(paths)}[/]")

    if all_imported and not no_commit:
        message = (
            f"feat(raw): import book — {paths[0].name}"
            if len(paths) == 1
            else f"feat(raw): import books — {len(all_imported)} artefato(s)"
        )
        commit(message, all_imported)

    compile_failures = []
    if compile_imported and all_written:
        from kb.compile import CompileBatchResult, compile_file, compile_many
        from kb.guardrails import SensitiveContentError, summarize_findings

        compiled_outputs = []
        if workers == 1:
            for chapter_path in all_written:
                try:
                    compiled_outputs.append(
                        compile_file(
                            chapter_path,
                            allow_sensitive=allow_sensitive,
                            no_commit=no_commit,
                        )
                    )
                except SensitiveContentError as exc:
                    typer.echo(summarize_findings(exc))
                    if allow_sensitive or typer.confirm(
                        "Continuar mesmo assim e enviar ao provider externo?",
                        default=False,
                    ):
                        compiled_outputs.append(
                            compile_file(
                                chapter_path,
                                allow_sensitive=True,
                                no_commit=no_commit,
                            )
                        )
                    else:
                        raise typer.Exit(code=1)

            if compiled_outputs:
                from kb.compile import update_index as do_update_index

                do_update_index(no_commit=no_commit)
        else:
            console.print(
                f"[dim]Compilando {len(all_written)} capítulo(s) com {workers} worker(s)...[/]"
            )
            result: CompileBatchResult = compile_many(
                all_written,
                workers=workers,
                allow_sensitive=allow_sensitive,
                no_commit=no_commit,
                update_index_enabled=True,
            )
            compiled_outputs = result.outputs
            compile_failures = result.failures

        typer.echo(f"{len(compiled_outputs)} capítulos compilados para wiki/")

        if compile_failures:
            console.print(
                f"\n[bold red]FALHAS DE COMPILAÇÃO: {len(compile_failures)}/{len(all_written)}[/]"
            )
            for failure in compile_failures:
                if isinstance(failure.error, SensitiveContentError):
                    detail = summarize_findings(failure.error)
                else:
                    detail = str(failure.error) or type(failure.error).__name__
                console.print(f"  [red]- {failure.raw_path.name}:[/] {detail}")

    if failed or (compile_imported and all_written and compile_failures):
        raise typer.Exit(code=1)


@app.command()
def compile(
    target: str = typer.Argument(
        None,
        help="Arquivo, diretório ou nome de livro (ex: 'Build a Large Language Model'); padrão: todos os arquivos em raw/",
    ),
    update_index: bool = typer.Option(True, help="Atualizar _index.md após compilar"),
    workers: int | None = typer.Option(
        None,
        "--workers",
        "-j",
        min=1,
        help="Número de arquivos compilados em paralelo (padrão: automático)",
    ),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão: escreve localmente sem commit; use --commit para versionar",
    ),
):
    """Compila raw/ → wiki/ usando LLM."""
    from kb.cmds.compile.run import execute_compile_command
    from kb.guardrails import SensitiveContentError, summarize_findings

    def _confirm_sensitive() -> bool:
        return typer.confirm(
            "Continuar mesmo assim e enviar ao provider externo?",
            default=False,
        )

    result = execute_compile_command(
        target=target,
        update_index=update_index,
        workers=workers,
        allow_sensitive=allow_sensitive,
        no_commit=no_commit,
        interactive_sensitive=True,
        confirm_sensitive=_confirm_sensitive,
    )

    for line in result.message_lines:
        if line:
            console.print(line)

    for out in result.compiled_outputs:
        rel = out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out
        console.print(f"  → [green]{rel}[/]")

    if result.failures:
        sensitive = [
            f for f in result.failures if isinstance(f.error, SensitiveContentError)
        ]
        for failure in sensitive:
            console.print(
                f"[yellow]{failure.raw_path.name}:[/] {summarize_findings(failure.error)}"
            )

    if result.exit_code != 0:
        raise typer.Exit(code=result.exit_code)

    if not result.compiled_outputs:
        raise typer.Exit()


@app.command()
def qa(
    question: str = typer.Argument(..., help="Pergunta para a knowledge base"),
    file_back: bool = typer.Option(
        False,
        "--file-back",
        "-f",
        help="Arquiva a resposta em outputs/ (use --to-wiki para arquivar na wiki)",
    ),
    to_wiki: bool = typer.Option(
        False, "--to-wiki", help="Arquiva a resposta em wiki/ em vez de outputs/"
    ),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão: escreve localmente sem commit; use --commit para versionar quando houver file-back",
    ),
    no_traverse: bool = typer.Option(
        False,
        "--no-traverse",
        help="Desativa traversal de wikilinks (usa apenas busca por palavra-chave)",
    ),
    depth: int = typer.Option(
        1,
        "--depth",
        help="Profundidade de traversal de wikilinks (padrão: 1; use --no-traverse para desativar)",
    ),
):
    """Responde uma pergunta consultando as fontes do kb."""
    from kb.cmds.qa.run import execute_qa_command
    from kb.guardrails import SensitiveContentError, summarize_findings

    console.print("[dim]Pesquisando nas fontes do kb...[/]\n")

    def _run_qa(allow_sensitive_flag: bool) -> None:
        response, saved = execute_qa_command(
            question=question,
            file_back=file_back,
            to_wiki=to_wiki,
            allow_sensitive=allow_sensitive_flag,
            no_commit=no_commit,
            no_traverse=no_traverse,
            depth=depth,
        )
        console.print(Markdown(response))
        if saved:
            console.print(f"\n[dim]Arquivado em:[/] [green]{saved}[/]")

    try:
        _run_qa(allow_sensitive)
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (
            allow_sensitive
            or typer.confirm(
                "Continuar mesmo assim e enviar ao provider externo?", default=False
            )
        ):
            raise typer.Exit(code=1)
        _run_qa(True)


@app.command()
def search(query: str = typer.Argument(..., help="Termos de busca")):
    """Busca artigos na wiki por palavra-chave."""
    from kb.cmds.search.run import execute_search_command

    lines = execute_search_command(query)
    for line in lines:
        console.print(line)
    if len(lines) == 1 and "Nenhum resultado" in lines[0]:
        raise typer.Exit()


@app.command()
def lint(
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
):
    """Executa health checks LLM sobre a wiki (relatório apenas)."""
    from kb.cmds.lint.run import execute_lint_command
    from kb.guardrails import SensitiveContentError, summarize_findings

    console.print("[dim]Auditando wiki...[/]\n")
    try:
        console.print(Markdown(execute_lint_command(allow_sensitive=allow_sensitive)))
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (
            allow_sensitive
            or typer.confirm(
                "Continuar mesmo assim e enviar ao provider externo?", default=False
            )
        ):
            raise typer.Exit(code=1)
        console.print(Markdown(execute_lint_command(allow_sensitive=True)))


@app.command()
def heal(
    n: int = typer.Option(
        10, "--n", "-n", help="Número de arquivos aleatórios a processar"
    ),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão: escreve localmente sem commit; use --commit para versionar",
    ),
):
    """Heal estocástico: pega N artigos aleatórios, corrige links, remove stubs, stampa reviewed."""
    from kb.guardrails import SensitiveContentError, summarize_findings
    from kb.heal import heal as do_heal

    console.print(f"[dim]Healing {n} arquivos aleatórios...[/]\n")
    try:
        log = do_heal(n, allow_sensitive=allow_sensitive, no_commit=no_commit)
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (
            allow_sensitive
            or typer.confirm(
                "Continuar mesmo assim e enviar ao provider externo?", default=False
            )
        ):
            raise typer.Exit(code=1)
        log = do_heal(n, allow_sensitive=True, no_commit=no_commit)
    if not log:
        console.print("[yellow]Wiki vazia.[/]")
        raise typer.Exit()
    for entry in log:
        icon = {
            "healed": "[green]✓[/]",
            "deleted_stub": "[red]✗[/]",
            "reviewed_no_changes": "[dim]·[/]",
        }.get(entry["action"], "?")
        console.print(f"  {icon} {entry['file']} [dim]({entry['action']})[/]")


@app.command()
def archive(
    stale: bool = typer.Option(
        False,
        "--stale",
        help="Move artigos stale (usa threshold de stale_pct do stats)",
    ),
    older_than: int = typer.Option(
        None,
        "--older-than",
        help="Move artigos não editados há N dias",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview sem mover arquivos",
    ),
):
    """Move artigos stale/órfãos de wiki/ para archive/."""
    from kb.archive import collect_candidates, move_to_archive
    from kb.config import ARCHIVE_DIR, WIKI_DIR

    try:
        candidates = collect_candidates(WIKI_DIR, stale=stale, older_than=older_than)
    except ValueError as exc:
        console.print(f"[red]Erro:[/] {exc}")
        raise typer.Exit(code=1) from None

    if not candidates:
        console.print("[dim]Nenhum artigo candidato a archive.[/]")
        raise typer.Exit()

    for c in candidates:
        try:
            rel = c["source"].relative_to(WIKI_DIR)
        except ValueError:
            console.print(f"[red]Erro:[/] caminho {c['source']} fora de {WIKI_DIR}")
            raise typer.Exit(code=1) from None
        c["dest"] = ARCHIVE_DIR / rel

    if dry_run:
        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        table.add_column("Arquivo", style="cyan")
        table.add_column("Motivo")
        table.add_column("Destino", justify="right")
        for c in candidates:
            rel = c["source"].relative_to(WIKI_DIR)
            dest_rel = (
                c["dest"].relative_to(ARCHIVE_DIR.parent)
                if c["dest"].is_relative_to(ARCHIVE_DIR.parent)
                else c["dest"]
            )
            table.add_row(str(rel), c["reason"], str(dest_rel))
        console.print(table)
        raise typer.Exit()

    log = move_to_archive(candidates, ARCHIVE_DIR, dry_run=False)
    for entry in log:
        if entry["action"] == "moved":
            console.print(f"  [green]→[/] {entry['dest']}")
        elif entry["action"] == "error":
            console.print(f"  [red]✗[/] {entry['source']} — {entry.get('detail', '')}")


@discovery_app.command("run")
def discovery_run(
    query: List[str] = typer.Option(
        None,
        "--query",
        help="Query de discovery (pode repetir; padrão usa queries canônicas).",
    ),
    max_per_source: int = typer.Option(
        2,
        "--max-per-source",
        help="Máximo de itens por fonte para cada query.",
    ),
    compile_after_ingest: bool = typer.Option(
        True,
        "--compile/--no-compile",
        help="Compilar automaticamente itens ingeridos quando houver KB_API_KEY.",
    ),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processamento sensível durante compile quando habilitado.",
    ),
    no_commit: bool = typer.Option(
        True,
        "--no-commit/--commit",
        help="Padrão local sem commit; use --commit para versionar arquivos gerados.",
    ),
):
    """Executa discovery + ingest com deduplicação por URLs já vistas."""
    from kb.discovery import run_scheduled_discovery

    if max_per_source < 1:
        console.print("[red]Erro:[/] --max-per-source deve ser >= 1.")
        raise typer.Exit(code=1)

    try:
        result = run_scheduled_discovery(
            queries=query or None,
            max_per_source=max_per_source,
            compile_after_ingest=compile_after_ingest,
            allow_sensitive=allow_sensitive,
            no_commit=no_commit,
        )
    except Exception as exc:
        console.print(f"[red]Erro no discovery:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[bold]Discovery concluído[/]")
    console.print(f"- queries: {', '.join(result.get('queries', []))}")
    console.print(f"- discovered: {result.get('discovered', 0)}")
    console.print(f"- ingested: {result.get('ingested', 0)}")
    console.print(f"- compiled: {result.get('compiled', 0)}")
    console.print(f"- skipped_seen: {result.get('skipped_seen', 0)}")
    console.print(f"- failures: {len(result.get('failures', []))}")
    console.print(f"- seen_urls_path: {result.get('seen_urls_path', '')}")


@jobs_app.command("list")
def jobs_list(
    show_cron: bool = typer.Option(
        True,
        "--show-cron/--hide-cron",
        help="Mostra comandos cron operacionais sugeridos.",
    ),
):
    """Lista jobs canônicos e seus cron hints."""
    from kb.jobs import (
        build_operational_cron_lines,
        get_jobs_list_rows,
        get_recommended_cron_chain,
    )

    for row in get_jobs_list_rows():
        extra = f" [dim]| {row['extra']}[/]" if row.get("extra") else ""
        console.print(
            f"[bold]{row['name']}[/] [dim]({row['schedule']})[/] — {row['description']}{extra}"
        )

    console.print("\n[bold]Cadeia sugerida (Fase 3):[/]")
    for item in get_recommended_cron_chain():
        console.print(
            f"  • [bold]{item['name']}[/] [dim]({item['schedule']})[/] — {item['purpose']}"
        )

    if show_cron:
        console.print("\n[bold]Cron operacional sugerido:[/]")
        for line in build_operational_cron_lines(
            executable="kb",
            stale_max_pct=20.0,
            disputed_max_pct=8.0,
        ):
            console.print(f"  {line}")


@jobs_app.command("run")
def jobs_run(
    name: str = typer.Argument(..., help="Nome do job a executar"),
    stale_max_pct: float = typer.Option(
        None,
        "--stale-max-pct",
        help="Falha o job health se stale_pct ultrapassar este limite.",
    ),
    disputed_max_pct: float = typer.Option(
        None,
        "--disputed-max-pct",
        help="Falha o job health se disputed_pct ultrapassar este limite.",
    ),
):
    """Executa um job canônico por nome."""
    from kb.jobs import HealthGateError, run_job

    try:
        console.print(
            run_job(
                name,
                stale_max_pct=stale_max_pct,
                disputed_max_pct=disputed_max_pct,
            )
        )
    except HealthGateError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1)


@jobs_app.command("gate")
def jobs_gate(
    stale_max_pct: float = typer.Option(
        20.0,
        "--stale-max-pct",
        help="Limite máximo de stale_pct para gate.",
    ),
    disputed_max_pct: float = typer.Option(
        8.0,
        "--disputed-max-pct",
        help="Limite máximo de disputed_pct para gate.",
    ),
):
    """Executa gate estrito de saúde para CI/pipeline (exit != 0 quando viola)."""
    from kb.jobs import run_health_gate

    code, message = run_health_gate(
        stale_max_pct=stale_max_pct,
        disputed_max_pct=disputed_max_pct,
    )
    if code != 0:
        console.print(f"[red]{message}[/]")
        raise typer.Exit(code=code)
    console.print(f"[green]{message}[/]")


@jobs_app.command("cron")
def jobs_cron(
    stale_max_pct: float = typer.Option(
        20.0,
        "--stale-max-pct",
        help="Limite de stale_pct embutido no comando health.",
    ),
    disputed_max_pct: float = typer.Option(
        8.0,
        "--disputed-max-pct",
        help="Limite de disputed_pct embutido no comando health.",
    ),
):
    """Imprime bloco de cron pronto para colar no crontab."""
    from kb.jobs import build_operational_cron_lines

    for line in build_operational_cron_lines(
        executable="python -m kb.cli",
        stale_max_pct=stale_max_pct,
        disputed_max_pct=disputed_max_pct,
    ):
        console.print(line)


@jobs_app.command("doc-gate")
def jobs_doc_gate(
    base_ref: str = typer.Option(
        "origin/main",
        "--base-ref",
        help="Ref base para calcular arquivos alterados.",
    ),
):
    """Falha se houver mudança em kb/*.py sem SPEC ou Handoff no diff."""
    from subprocess import run
    from kb.doc_gate import evaluate_doc_gate

    proc = run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        message = "Falha ao calcular diff para doc-gate"
        if stderr:
            message = f"{message}: {stderr}"
        console.print(f"[red]{message}[/]")
        raise typer.Exit(code=1)

    changed = [
        line.strip() for line in (proc.stdout or "").splitlines() if line.strip()
    ]
    result = evaluate_doc_gate(changed)

    if result.ok:
        console.print(f"[green]{result.reason}[/]")
        return

    console.print(f"[red]{result.reason}[/]")
    raise typer.Exit(code=1)


@handoff_app.command("create")
def handoff_create(
    scope: str = typer.Option(..., "--scope", help="Escopo da sessão."),
    summary: str = typer.Option("", "--summary", help="Resumo das entregas."),
    next_steps: str = typer.Option("", "--next-steps", help="Próximos passos."),
    evidence: str = typer.Option("", "--evidence", help="Evidências executadas."),
    decisions: str = typer.Option("", "--decisions", help="Decisões tomadas."),
):
    """Cria handoff estruturado em docs/handoffs/YYYY-MM-DD-HHMM.md."""
    from subprocess import run
    from kb.handoff import create_handoff

    branch = ""
    try:
        proc = run(
            ["git", "branch", "--show-current"],
            check=False,
            capture_output=True,
            text=True,
        )
        branch = (proc.stdout or "").strip()
    except Exception:
        branch = ""

    path = create_handoff(
        scope=scope,
        summary=summary,
        branch=branch,
        next_steps=next_steps,
        evidence=evidence,
        decisions=decisions,
    )
    console.print(f"[green]Handoff criado:[/] {path}")
