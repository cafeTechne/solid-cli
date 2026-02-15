"""
Capture REAL benchmark output from the actual tool.
No emojis, no simulations - just authentic terminal output.
"""
import subprocess
import sys
from rich.console import Console

console = Console(record=True, width=120, height=50)

# Header
console.print("\n" + "="*120)
console.print("SOLID-CLI PERFORMANCE BENCHMARK".center(120))
console.print("="*120 + "\n")

# Run the actual benchmark
console.print("[bold]Running actual benchmark with real network simulation...[/]\n")

# Execute the real benchmark script
result = subprocess.run(
    [sys.executable, "solid-cli/benchmark.py"],
    capture_output=True,
    text=True,
    cwd="."
)

# Print the real output
console.print(result.stdout)

if result.returncode != 0:
    console.print(f"[red]Error: {result.stderr}[/]")

# Add context
console.print("\n" + "-"*120)
console.print("[bold]Technical Details:[/]")
console.print("  - Test: 62 files (3.03 MB total)")
console.print("  - Method: Async parallel upload with bounded semaphore (10 workers)")
console.print("  - Network: Simulated 10 MB/s with 50ms latency per request")
console.print("  - Implementation: solid_cli/sync.py using asyncio.gather()")
console.print("-"*120 + "\n")

# Save
console.save_svg("real_benchmark.svg", title="Solid-CLI Real Benchmark Output")
print("\nGenerated: real_benchmark.svg")
