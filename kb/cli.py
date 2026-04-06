"""CLI principal do kb."""

import typer
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="LLM-powered personal knowledge base")
jobs_app = typer.Typer(help="Jobs canônicos e agendáveis do kb")
app.add_typer(jobs_app, name="jobs")
console = Console()


@app.command()
def ingest(path: Path = typer.Argument(..., help="Arquivo para adicionar a raw/")):
    """Copia um arquivo para raw/."""
    from kb.config import RAW_DIR
    from kb.state import record_ingest

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / path.name
    dest.write_bytes(path.read_bytes())
    record_ingest(dest)
    console.print(f"[green]Adicionado:[/] {dest}")


@app.command("import-book")
def import_book(
    path: Path = typer.Argument(..., help="Arquivo EPUB ou PDF textual para importar em capítulos Markdown"),
    output: Path = typer.Option(None, "--output", help="Diretório de saída (padrão: raw/books/<livro>)"),
    compile_imported: bool = typer.Option(False, "--compile", help="Compilar os capítulos importados para wiki/ após a importação"),
    allow_sensitive: bool = typer.Option(False, "--allow-sensitive", help="Permite processar conteúdo sensível sem confirmação adicional"),
    no_commit: bool = typer.Option(False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"),
):
    """Importa um livro EPUB ou PDF textual para raw/books/ em arquivos Markdown por capítulo."""
    from kb.book_import import BookImportError, default_output_dir, import_epub

    target_dir = output or default_output_dir(path)

    try:
        written_files, metadata_path = import_epub(path, target_dir)
    except (BookImportError, PermissionError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{len(written_files)} capítulos importados em {target_dir} (metadata: {metadata_path.name})")

    if compile_imported:
        from kb.compile import compile_file, update_index as do_update_index
        from kb.guardrails import SensitiveContentError, summarize_findings

        compiled_outputs = []
        for chapter_path in written_files:
            try:
                compiled_outputs.append(compile_file(chapter_path, allow_sensitive=allow_sensitive, no_commit=no_commit))
            except SensitiveContentError as exc:
                typer.echo(summarize_findings(exc))
                if allow_sensitive or typer.confirm("Continuar mesmo assim e enviar ao provider externo?", default=False):
                    compiled_outputs.append(compile_file(chapter_path, allow_sensitive=True, no_commit=no_commit))
                else:
                    raise typer.Exit(code=1)
        do_update_index(no_commit=no_commit)
        typer.echo(f"{len(compiled_outputs)} capítulos compilados para wiki/")


@app.command()
def compile(
    file: Path = typer.Argument(None, help="Arquivo específico em raw/ (padrão: todos)"),
    update_index: bool = typer.Option(True, help="Atualizar _index.md após compilar"),
    allow_sensitive: bool = typer.Option(False, "--allow-sensitive", help="Permite processar conteúdo sensível sem confirmação adicional"),
    no_commit: bool = typer.Option(False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"),
):
    """Compila raw/ → wiki/ usando LLM."""
    from kb.compile import compile_file, discover_compile_targets, update_index as do_update_index
    from kb.guardrails import SensitiveContentError, summarize_findings

    targets = discover_compile_targets(file)

    if not targets:
        console.print("[yellow]Nenhum arquivo em raw/[/]")
        raise typer.Exit()

    for t in targets:
        console.print(f"Compilando [bold]{t.name}[/]...")
        try:
            out = compile_file(t, allow_sensitive=allow_sensitive, no_commit=no_commit)
        except SensitiveContentError as exc:
            console.print(f"[yellow]{summarize_findings(exc)}[/]")
            if allow_sensitive or typer.confirm("Continuar mesmo assim e enviar ao provider externo?", default=False):
                out = compile_file(t, allow_sensitive=True, no_commit=no_commit)
            else:
                raise typer.Exit(code=1)
        rel = out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out
        console.print(f"  → [green]{rel}[/]")

    if update_index:
        do_update_index(no_commit=no_commit)
        console.print("[dim]Índice atualizado.[/]")


@app.command()
def qa(
    question: str = typer.Argument(..., help="Pergunta para a knowledge base"),
    file_back: bool = typer.Option(False, "--file-back", "-f", help="Arquiva a resposta de volta na wiki"),
    allow_sensitive: bool = typer.Option(False, "--allow-sensitive", help="Permite processar conteúdo sensível sem confirmação adicional"),
    no_commit: bool = typer.Option(False, "--no-commit", help="Escreve arquivos localmente sem criar commit git quando houver file-back"),
    no_traverse: bool = typer.Option(False, "--no-traverse", help="Desativa traversal de wikilinks (usa apenas busca por palavra-chave)"),
    depth: int = typer.Option(1, "--depth", help="Profundidade de traversal de wikilinks (padrão: 1; use --no-traverse para desativar)"),
):
    """Responde uma pergunta consultando as fontes do kb."""
    from kb.guardrails import SensitiveContentError, summarize_findings

    console.print("[dim]Pesquisando nas fontes do kb...[/]\n")

    def _run_qa(allow_sensitive_flag: bool) -> None:
        traverse = not no_traverse

        if file_back:
            from kb.qa import answer_and_file

            response, saved = answer_and_file(question, allow_sensitive=allow_sensitive_flag, no_commit=no_commit)
            console.print(Markdown(response))
            if saved:
                console.print(f"\n[dim]Arquivado em:[/] [green]{saved}[/]")
            return

        from kb.qa import answer

        console.print(Markdown(answer(question, allow_sensitive=allow_sensitive_flag, traverse=traverse, depth=depth)))

    try:
        _run_qa(allow_sensitive)
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (allow_sensitive or typer.confirm("Continuar mesmo assim e enviar ao provider externo?", default=False)):
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
        rel = r["path"].relative_to(Path.cwd()) if r["path"].is_relative_to(Path.cwd()) else r["path"]
        console.print(f"[bold]{r['path'].stem}[/] [dim]({rel})[/] score={r['score']}")
        if r["snippet"]:
            console.print(f"  [dim]{r['snippet'][:120]}[/]")


@app.command()
def lint(
    allow_sensitive: bool = typer.Option(False, "--allow-sensitive", help="Permite processar conteúdo sensível sem confirmação adicional"),
):
    """Executa health checks LLM sobre a wiki (relatório apenas)."""
    from kb.guardrails import SensitiveContentError, summarize_findings
    from kb.lint import lint_wiki

    console.print("[dim]Auditando wiki...[/]\n")
    try:
        console.print(Markdown(lint_wiki(allow_sensitive=allow_sensitive)))
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (allow_sensitive or typer.confirm("Continuar mesmo assim e enviar ao provider externo?", default=False)):
            raise typer.Exit(code=1)
        console.print(Markdown(lint_wiki(allow_sensitive=True)))


@app.command()
def heal(
    n: int = typer.Option(10, "--n", "-n", help="Número de arquivos aleatórios a processar"),
    allow_sensitive: bool = typer.Option(False, "--allow-sensitive", help="Permite processar conteúdo sensível sem confirmação adicional"),
    no_commit: bool = typer.Option(False, "--no-commit", help="Escreve arquivos localmente sem criar commit git"),
):
    """Heal estocástico: pega N artigos aleatórios, corrige links, remove stubs, stampa reviewed."""
    from kb.guardrails import SensitiveContentError, summarize_findings
    from kb.heal import heal as do_heal

    console.print(f"[dim]Healing {n} arquivos aleatórios...[/]\n")
    try:
        log = do_heal(n, allow_sensitive=allow_sensitive, no_commit=no_commit)
    except SensitiveContentError as exc:
        console.print(f"[yellow]{summarize_findings(exc)}[/]")
        if not (allow_sensitive or typer.confirm("Continuar mesmo assim e enviar ao provider externo?", default=False)):
            raise typer.Exit(code=1)
        log = do_heal(n, allow_sensitive=True, no_commit=no_commit)
    if not log:
        console.print("[yellow]Wiki vazia.[/]")
        raise typer.Exit()
    for entry in log:
        icon = {"healed": "[green]✓[/]", "deleted_stub": "[red]✗[/]", "reviewed_no_changes": "[dim]·[/]"}.get(
            entry["action"], "?"
        )
        console.print(f"  {icon} {entry['file']} [dim]({entry['action']})[/]")


@jobs_app.command("list")
def jobs_list():
    """Lista jobs canônicos e seus cron hints."""
    from kb.jobs import list_jobs

    for job in list_jobs():
        console.print(f"[bold]{job.name}[/] [dim]({job.schedule})[/] — {job.description}")


@jobs_app.command("run")
def jobs_run(name: str = typer.Argument(..., help="Nome do job a executar")):
    """Executa um job canônico por nome."""
    from kb.jobs import run_job

    console.print(run_job(name))
