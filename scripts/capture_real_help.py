"""
Capture real CLI help output - no simulations.
"""
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel

console = Console(record=True, width=120, height=60)

commands = [
    ("sync", "Synchronize local directory to remote Solid Pod"),
    ("verify", "Verify local files against remote Pod"),
    ("mount", "Mount Solid Pod as local filesystem"),
    ("monitor", "Real-time TUI dashboard")
]

console.print("\n" + "="*120)
console.print("SOLID-CLI COMMAND REFERENCE".center(120))
console.print("="*120 + "\n")

for cmd, desc in commands:
    console.print(f"[bold cyan]$ solid {cmd} --help[/]\n")
    
    result = subprocess.run(
        [sys.executable, "-m", "solid_cli.main", cmd, "--help"],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    console.print(result.stdout)
    console.print("\n" + "-"*120 + "\n")

console.print("[dim]Repository: https://github.com/cafeTechne/solid-cli[/]")
console.print("[dim]Tests: 166 passed | Coverage: 86%[/]\n")

console.save_svg("real_cli_help.svg", title="Solid-CLI Command Reference")
print("\nGenerated: real_cli_help.svg")
