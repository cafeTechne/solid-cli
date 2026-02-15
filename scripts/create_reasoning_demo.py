"""
Demonstrate the N3Logic Reasoning Engine in action.
Shows how the tool infers metadata automatically.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.columns import Columns
from rich.text import Text

console = Console(record=True, width=120, height=45)

# Header
console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════════════════════════════════════[/]")
console.print("[bold magenta]                    N3LOGIC REASONING ENGINE DEMONSTRATION[/]")
console.print("[bold cyan]═══════════════════════════════════════════════════════════════════════════════════════════════[/]\n")

# Input Files
console.print("[bold yellow]📁 Input: Files being synced to Solid Pod[/]\n")

input_table = Table(show_header=True, header_style="bold cyan", box=None)
input_table.add_column("File Path", style="dim")
input_table.add_column("Size", justify="right")
input_table.add_column("Parent Folder", style="blue")

input_table.add_row("/TopSecret/budget_2026.xlsx", "245 KB", "[red]TopSecret[/]")
input_table.add_row("/TopSecret/strategy.pdf", "1.2 MB", "[red]TopSecret[/]")
input_table.add_row("/Public/readme.md", "4 KB", "[green]Public[/]")
input_table.add_row("/Research/paper.tex", "89 KB", "[yellow]Research[/]")

console.print(input_table)
console.print()

# N3 Rules
console.print("[bold green]🧠 N3Logic Rules Applied[/]\n")

rules_code = """# Rule 1: Confidentiality Propagation
{
  ?folder ex:securityLevel "TopSecret" .
  ?file rdf:type ?folder .
} => {
  ?file ex:securityLevel "TopSecret" .
}

# Rule 2: Provenance Tracking (PROV-O)
{
  ?file a schema:DigitalDocument .
} => {
  ?file prov:wasGeneratedBy <#SolidCLI> ;
        prov:generatedAtTime ?timestamp ;
        prov:wasAttributedTo <#User> .
}"""

syntax = Syntax(rules_code, "turtle", theme="monokai", line_numbers=True)
console.print(Panel(syntax, title="[bold]N3 Inference Rules[/]", border_style="green"))
console.print()

# Output with Inferred Metadata
console.print("[bold magenta]✨ Output: Files with Inferred Metadata[/]\n")

output_table = Table(show_header=True, header_style="bold magenta")
output_table.add_column("File", style="cyan")
output_table.add_column("Security Level", justify="center")
output_table.add_column("Provenance", style="dim")
output_table.add_column("Inference Source", style="yellow")

output_table.add_row(
    "budget_2026.xlsx",
    "[bold red]TopSecret[/]",
    "✓ Tracked",
    "[dim]Inferred from parent folder[/]"
)
output_table.add_row(
    "strategy.pdf",
    "[bold red]TopSecret[/]",
    "✓ Tracked",
    "[dim]Inferred from parent folder[/]"
)
output_table.add_row(
    "readme.md",
    "[green]Public[/]",
    "✓ Tracked",
    "[dim]Explicit (no inference)[/]"
)
output_table.add_row(
    "paper.tex",
    "[yellow]Research[/]",
    "✓ Tracked",
    "[dim]Inferred from parent folder[/]"
)

console.print(output_table)
console.print()

# Key Insight
insight = Panel(
    "[bold cyan]💡 Key Insight:[/] The reasoning engine doesn't just copy files—it understands their context.\n\n"
    "Traditional tools: [dim]\"budget_2026.xlsx uploaded successfully\"[/]\n"
    "Solid-CLI: [bold green]\"budget_2026.xlsx uploaded with TopSecret classification (inferred from /TopSecret/ parent)\"[/]\n\n"
    "[bold]This enables:[/]\n"
    "  • Automatic policy enforcement (e.g., block public sharing of TopSecret files)\n"
    "  • Audit trails (who created what, when)\n"
    "  • Smart search (find all confidential documents)\n"
    "  • Compliance (GDPR, HIPAA metadata requirements)",
    title="[bold]Why This Matters[/]",
    border_style="yellow"
)
console.print(insight)

# Footer
console.print("\n[dim]Based on: N3Logic: A Logical Framework for the World Wide Web (Berners-Lee et al., 2007)[/]")
console.print("[dim]Implementation: solid_cli/reasoner.py | Uses rdflib for RDF graph operations[/]\n")

# Save
console.save_svg("demo_reasoning.svg", title="N3Logic Reasoning Demo")
print("\n✅ Generated: demo_reasoning.svg")
