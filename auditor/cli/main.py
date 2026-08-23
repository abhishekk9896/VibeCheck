import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from auditor.core.agent import build_auditor_graph, AuditorState
from auditor.core.report_generator import ReportGenerator

console = Console()
app = typer.Typer(
    name="scope-auditor",
    help="Scope & Quality Auditor Agent for vibe-coded Python projects.",
)


@app.command()
def init():
    """Initializes a baseline SCOPE.md if missing."""
    console.print(Panel("[bold green]Scope Auditor CLI initialized successfully.[/bold green]", title="Scope Auditor"))


@app.command()
def audit(
    scope_path: str = typer.Option("SCOPE.md", "--scope", "-s", help="Path to SCOPE.md"),
    root_dir: str = typer.Option(".", "--root", "-r", help="Target project root directory"),
    export: bool = typer.Option(False, "--export", "-e", help="Export Markdown and HTML report files"),
):
    """Run scope drift, quality audit, and self-correction via LangGraph."""
    console.print(Panel(f"[bold blue]Starting Scope Auditor Graph[/bold blue]\nTarget: [white]{root_dir}[/white] | Spec: [white]{scope_path}[/white]", title="Scope Auditor"))

    initial_state: AuditorState = {
        "root_dir": root_dir,
        "scope_path": scope_path,
        "requirements": [],
        "ast_maps": [],
        "lint_issues": [],
        "test_failures": [],
        "total_tests": 0,
        "passed_tests": 0,
        "drift_report": None,
        "iterations": 0,
        "status": "init",
    }

    graph = build_auditor_graph()

    with console.status("[bold green]Executing LangGraph workflow & self-correction loop..."):
        final_state = graph.invoke(initial_state)

    # Output Summary Table
    table = Table(title="Audit Execution Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Requirements Parsed", str(len(final_state["requirements"])))
    table.add_row("Source Files AST Mapped", str(len(final_state["ast_maps"])))
    table.add_row("Ruff Lint Issues", f"[green]{len(final_state['lint_issues'])}[/green]" if len(final_state['lint_issues']) == 0 else f"[red]{len(final_state['lint_issues'])}[/red]")
    table.add_row("Pytest Pass Rate", f"[bold green]{final_state['passed_tests']}/{final_state['total_tests']}[/bold green]")
    
    missing_reqs = len(final_state["drift_report"].missing_requirements) if final_state["drift_report"] else 0
    table.add_row("Scope Drift (Missing)", f"[green]{missing_reqs}[/green]" if missing_reqs == 0 else f"[red]{missing_reqs}[/red]")
    table.add_row("Remediation Loops Run", str(final_state.get("iterations", 0)))

    console.print(table)

    if export:
        gen = ReportGenerator(final_state, output_dir=root_dir)
        md_file = gen.generate_markdown()
        html_file = gen.generate_html()
        console.print(f"\n[bold green]✓ Exported Reports:[/bold green]\n - {md_file}\n - {html_file}")

    if final_state["passed_tests"] == final_state["total_tests"] and missing_reqs == 0 and len(final_state["lint_issues"]) == 0:
        console.print("\n[bold green]✓ Codebase is fully compliant with SCOPE.md![/bold green]\n")
    else:
        console.print("\n[bold yellow]⚠ Audit finished with unresolved issues.[/bold yellow]\n")


if __name__ == "__main__":
    app()