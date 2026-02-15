"""Theme and styling utilities for Solid CLI."""

from rich.console import Console
import pyfiglet

COLOR_PRIMARY = "bold cyan"
COLOR_SECONDARY = "bold magenta"


def print_banner() -> None:
    """Print the Solid CLI banner using pyfiglet and rich."""
    console = Console()
    banner_text = pyfiglet.figlet_format("SOLID CLI", font="slant")
    console.print(banner_text, style=COLOR_PRIMARY)
