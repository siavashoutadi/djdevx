import difflib
from rich.console import Console as RichConsole
from rich.text import Text


class PrintConsole:
    """Styled output printer for djdevx messages."""

    def __init__(self):
        self._console = RichConsole()

    def step(self, line: str):
        """Print a step message in cyan."""
        self._console.print(f"[bold cyan]{line}[/bold cyan]")

    def success(self, line: str):
        """Print a success message in green."""
        self._console.print(f"[bold green]{line}[/bold green]")

    def error(self, line: str):
        """Print an error message in red."""
        self._console.print(f"[bold red]{line}[/bold red]")

    def info(self, line: str):
        """Print an info message without styling."""
        self._console.print(f"{line}")

    def warning(self, line: str):
        """Print a warning message in yellow."""
        self._console.print(f"[bold yellow]{line}[/bold yellow]")

    def list(self, items: list):
        """Print a list of items with bullet points."""
        for item in items:
            self._console.print(f"🔹[bold]{item}[/bold]")

    def diff(self, old: str, new: str, title_old="(current)", title_new="(new)"):
        """Print a diff comparison between old and new content."""
        self._console.print(f"[bold cyan]Diff: {title_old} -> {title_new}[/bold cyan]")

        for line in difflib.ndiff(
            old.splitlines(keepends=False),
            new.splitlines(keepends=False),
        ):
            prefix, body = line[:2], line[2:]
            if prefix == "- ":
                self._console.print(Text("- " + body, style="on red"))
            elif prefix == "+ ":
                self._console.print(Text("+ " + body, style="on green"))
            elif prefix == "  ":
                self._console.print("  " + body)


# Create default instance for easy importing
console = PrintConsole()
