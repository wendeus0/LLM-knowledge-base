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

app = typer.Typer(help="LLM-powered personal knowledge base")
jobs_app = typer.Typer(help="Jobs canônicos e agendáveis do kb")
app.add_typer(jobs_app, name="jobs")
console = Console()


@app.command()
def ingest(
    sources: list[str] = typer.Argument(
        ..., help="Arquivo(s) ou URL(s) para adicionar a raw/"
    ),
    no_commit: bool = typer.Option(
        False, "--no-commit", help="Escreve arquivo localmente sem criar commit git"
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
        False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"
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

    all_written: List[Path] = []
    results_map = {}  # path → (status, detail) para manter ordem original na tabela

    def _process(path: Path):
        target_dir = (output if len(paths) == 1 else None) or default_output_dir(path)
        if not force and target_dir.exists() and any(target_dir.glob("*.md")):
            return path, "skip", target_dir
        try:
            written_files, _ = import_epub(
                path, target_dir, use_ocr=ocr, chunk_pages=chunk_pages
            )
            return path, "ok", written_files
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
            all_written.extend(detail)
            output_dir = detail[0].parent if detail else None
            detail_label = f"[dim]{len(detail)} capítulos[/]"
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
            typer.echo(str(detail[0].parent))
        elif status == "skip":
            typer.echo(str(detail))

    failed = [p for p in paths if results_map[p][0] == "fail"]
    if failed:
        console.print(f"\n[bold red]FALHAS: {len(failed)}/{len(paths)}[/]")

    if compile_imported and all_written:
        from kb.compile import compile_file, update_index as do_update_index
        from kb.guardrails import SensitiveContentError, summarize_findings

        compiled_outputs = []
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
                    "Continuar mesmo assim e enviar ao provider externo?", default=False
                ):
                    compiled_outputs.append(
                        compile_file(
                            chapter_path, allow_sensitive=True, no_commit=no_commit
                        )
                    )
                else:
                    raise typer.Exit(code=1)
        do_update_index(no_commit=no_commit)
        typer.echo(f"{len(compiled_outputs)} capítulos compilados para wiki/")

    if failed:
        raise typer.Exit(code=1)


@app.command()
def compile(
    target: str = typer.Argument(
        None,
        help="Arquivo, diretório ou nome de livro (ex: 'Build a Large Language Model'); padrão: todos os arquivos em raw/",
    ),
    update_index: bool = typer.Option(True, help="Atualizar _index.md após compilar"),
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
    no_commit: bool = typer.Option(
        False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"
    ),
):
    """Compila raw/ → wiki/ usando LLM."""
    from kb.compile import (
        compile_file,
        discover_compile_targets,
        find_book_dirs,
        update_index as do_update_index,
    )
    from kb.guardrails import SensitiveContentError, summarize_findings

    if target is None:
        targets = discover_compile_targets()
    else:
        path = Path(target)
        if path.exists():
            targets = discover_compile_targets(path)
        else:
            book_dirs = find_book_dirs(target)
            if not book_dirs:
                console.print(f"[red]Nenhum livro encontrado para:[/] {target}")
                raise typer.Exit(code=1)
            targets = []
            for d in book_dirs:
                targets.extend(discover_compile_targets(d))
            console.print(
                f"[dim]{len(book_dirs)} livro(s), {len(targets)} arquivo(s) a compilar[/]"
            )

    if not targets:
        console.print("[yellow]Nenhum arquivo em raw/[/]")
        raise typer.Exit()

    compiled_outputs = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Compilando...[/] {task.completed}/{task.total}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("{task.fields[current]}", justify="right"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("", total=len(targets), current="")

        for t in targets:
            progress.update(task, current=f"[dim]{t.name}[/]")
            try:
                out = compile_file(
                    t, allow_sensitive=allow_sensitive, no_commit=no_commit
                )
            except SensitiveContentError as exc:
                progress.stop()
                console.print(f"[yellow]{summarize_findings(exc)}[/]")
                if allow_sensitive or typer.confirm(
                    "Continuar mesmo assim e enviar ao provider externo?", default=False
                ):
                    out = compile_file(t, allow_sensitive=True, no_commit=no_commit)
                else:
                    raise typer.Exit(code=1)
                progress.start()
            compiled_outputs.append(out)
            progress.advance(task)

    for out in compiled_outputs:
        rel = out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out
        console.print(f"  → [green]{rel}[/]")

    if update_index:
        do_update_index(no_commit=no_commit)
        console.print("[dim]Índice atualizado.[/]")


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
        False,
        "--no-commit",
        help="Escreve arquivos localmente sem criar commit git quando houver file-back",
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
    from kb.guardrails import SensitiveContentError, summarize_findings

    console.print("[dim]Pesquisando nas fontes do kb...[/]\n")

    def _run_qa(allow_sensitive_flag: bool) -> None:
        traverse = not no_traverse

        if file_back:
            from kb.qa import answer_and_file

            response, saved = answer_and_file(
                question,
                allow_sensitive=allow_sensitive_flag,
                no_commit=no_commit,
                to_wiki=to_wiki,
                traverse=traverse,
                depth=depth,
            )
            console.print(Markdown(response))
            if saved:
                console.print(f"\n[dim]Arquivado em:[/] [green]{saved}[/]")
            return

        from kb.qa import answer

        console.print(
            Markdown(
                answer(
                    question,
                    allow_sensitive=allow_sensitive_flag,
                    traverse=traverse,
                    depth=depth,
                )
            )
        )

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
    from kb.search import search as do_search

    results = do_search(query)
    if not results:
        console.print("[yellow]Nenhum resultado encontrado.[/]")
        raise typer.Exit()
    for r in results:
        rel = (
            r["path"].relative_to(Path.cwd())
            if r["path"].is_relative_to(Path.cwd())
            else r["path"]
        )
        console.print(f"[bold]{r['path'].stem}[/] [dim]({rel})[/] score={r['score']}")
        if r["snippet"]:
            console.print(f"  [dim]{r['snippet'][:120]}[/]")


@app.command()
def lint(
    allow_sensitive: bool = typer.Option(
        False,
        "--allow-sensitive",
        help="Permite processar conteúdo sensível sem confirmação adicional",
    ),
):
    """Executa health checks LLM sobre a wiki (relatório apenas)."""
    from kb.guardrails import SensitiveContentError, summarize_findings
    from kb.lint import lint_wiki

    console.print("[dim]Auditando wiki...[/]\n")
    try:
        console.print(Markdown(lint_wiki(allow_sensitive=allow_sensitive)))
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (
            allow_sensitive
            or typer.confirm(
                "Continuar mesmo assim e enviar ao provider externo?", default=False
            )
        ):
            raise typer.Exit(code=1)
        console.print(Markdown(lint_wiki(allow_sensitive=True)))


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
        False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"
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


@jobs_app.command("list")
def jobs_list():
    """Lista jobs canônicos e seus cron hints."""
    from kb.jobs import list_jobs

    for job in list_jobs():
        console.print(
            f"[bold]{job.name}[/] [dim]({job.schedule})[/] — {job.description}"
        )


@jobs_app.command("run")
def jobs_run(name: str = typer.Argument(..., help="Nome do job a executar")):
    """Executa um job canônico por nome."""
    from kb.jobs import run_job

    console.print(run_job(name))
