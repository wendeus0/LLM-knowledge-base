"""CLI principal do kb."""

import typer
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="LLM-powered personal knowledge base")
console = Console()


@app.command()
def ingest(path: Path = typer.Argument(..., help="Arquivo para adicionar a raw/")):
    """Copia um arquivo para raw/."""
    from kb.config import RAW_DIR
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / path.name
    dest.write_bytes(path.read_bytes())
    console.print(f"[green]Adicionado:[/] {dest}")


@app.command()
def compile(
    file: Path = typer.Argument(None, help="Arquivo específico em raw/ (padrão: todos)"),
    update_index: bool = typer.Option(True, help="Atualizar _index.md após compilar"),
):
    """Compila raw/ → wiki/ usando LLM."""
    from kb.config import RAW_DIR
    from kb.compile import compile_file, update_index as do_update_index

    targets = [file] if file else list(RAW_DIR.iterdir())
    targets = [t for t in targets if t.is_file()]

    if not targets:
        console.print("[yellow]Nenhum arquivo em raw/[/]")
        raise typer.Exit()

    for t in targets:
        console.print(f"Compilando [bold]{t.name}[/]...")
        out = compile_file(t)
        console.print(f"  → [green]{out.relative_to(Path.cwd())}[/]")

    if update_index:
        do_update_index()
        console.print("[dim]Índice atualizado.[/]")


@app.command()
def qa(
    question: str = typer.Argument(..., help="Pergunta para a knowledge base"),
    file_back: bool = typer.Option(False, "--file-back", "-f", help="Arquiva a resposta de volta na wiki"),
):
    """Responde uma pergunta consultando a wiki."""
    console.print("[dim]Pesquisando na wiki...[/]\n")

    if file_back:
        from kb.qa import answer_and_file
        response, saved = answer_and_file(question)
        console.print(Markdown(response))
        if saved:
            console.print(f"\n[dim]Arquivado em:[/] [green]{saved}[/]")
    else:
        from kb.qa import answer
        console.print(Markdown(answer(question)))


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
def lint():
    """Executa health checks LLM sobre a wiki (relatório apenas)."""
    from kb.lint import lint_wiki
    console.print("[dim]Auditando wiki...[/]\n")
    console.print(Markdown(lint_wiki()))


@app.command()
def heal(
    n: int = typer.Option(10, "--n", "-n", help="Número de arquivos aleatórios a processar"),
):
    """Heal estocástico: pega N artigos aleatórios, corrige links, remove stubs, stampa reviewed."""
    from kb.heal import heal as do_heal
    console.print(f"[dim]Healing {n} arquivos aleatórios...[/]\n")
    log = do_heal(n)
    if not log:
        console.print("[yellow]Wiki vazia.[/]")
        raise typer.Exit()
    for entry in log:
        icon = {"healed": "[green]✓[/]", "deleted_stub": "[red]✗[/]", "reviewed_no_changes": "[dim]·[/]"}.get(
            entry["action"], "?"
        )
        console.print(f"  {icon} {entry['file']} [dim]({entry['action']})[/]")
