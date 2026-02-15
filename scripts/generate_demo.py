import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

console = Console(record=True, width=100, height=30)

def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    return layout

def make_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        "[b magenta]Solid-CLI[/] [dim]Privacy-Preserving Agent[/]",
        "[bold cyan]v1.0.0[/]"
    )
    return Panel(grid, style="white on blue")

def make_body(status, files):
    table = Table(expand=True, show_header=True, header_style="bold magenta")
    table.add_column("File", ratio=4)
    table.add_column("Status", ratio=2)
    table.add_column("Reasoning Inference", ratio=4)

    for file, state, inference in files:
        table.add_row(file, state, inference)
    
    return Panel(table, title=f"Sync Status: {status}", border_style="green")

def make_footer():
    return Panel("[dim]Press Ctrl+C to exit | [bold]N3Logic Engine Active[/] | [d]Provo-O Tracking[/]", style="white on blue")

layout = generate_layout()
layout["header"].update(make_header())
layout["footer"].update(make_footer())

files_data = [
    ("secret_plans.pdf", "[green]Synced[/]", "[bold red]CONFIDENTIAL[/] (Inferred from Parent Folder)"),
    ("budget_2026.xlsx", "[green]Synced[/]", "[yellow]Finance Dept[/] (Inferred from Creator)"),
    ("meeting_notes.md", "[blue]Processing...[/]", "Extracting Entities..."),
]

with Live(layout, console=console, refresh_per_second=4):
    for i in range(10):
        if i == 3:
             files_data[2] = ("meeting_notes.md", "[green]Synced[/]", "[cyan]Project: Solid[/] (Inferred from Content)")
             files_data.append(("research_paper.tex", "[blue]Uploading[/]", " ... "))
        
        layout["body"].update(make_body("Active", files_data))
        time.sleep(0.2)

layout["body"].update(make_body("Idle", files_data))
console.print(layout)

console.save_svg("cover.svg", title="Solid-CLI Demo")
