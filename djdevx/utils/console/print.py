import difflib
from rich.console import Console as RichConsole
from rich.markup import escape
from rich.table import Table
from rich.text import Text

CHECK_MARK = "\u2713"
CROSS_MARK = "\u2717"
ELLIPSIS = "\u2026"

GREEN_CHECK_MARK = f"[bold green]{CHECK_MARK}[/bold green]"
RED_CROSS_MARK = f"[bold red]{CROSS_MARK}[/bold red]"


class PrintConsole:
    """Styled output printer for djdevx messages."""

    def __init__(self):
        self._console = RichConsole()

    def step(self, line: str):
        """Print a pending step with a blue checkbox."""
        self._console.print(f"[bold blue]\u2610[/bold blue] {escape(line)}")

    def step_done(self, line: str):
        """Print a completed step with a blue checked box."""
        self._console.print(f"[bold blue]\u2611[/bold blue] {escape(line)}")

    def success(self, line: str, end: str = "\n"):
        """Print a success message in green."""
        self._console.print(f"[bold green]{escape(line)}[/bold green]", end=end)

    def error(self, line: str, end: str = "\n"):
        """Print an error message in red."""
        self._console.print(f"[bold red]{escape(line)}[/bold red]", end=end)

    def info(self, line: str, end: str = "\n"):
        """Print an info message without styling."""
        self._console.print(escape(line), end=end)

    def warning(self, line: str):
        """Print a warning message in yellow."""
        self._console.print(f"[bold yellow]{escape(line)}[/bold yellow]")

    def ok(self, message: str):
        """Print a green checkmark followed by an unstyled message on the same line."""
        self._console.print(f"[bold green]{CHECK_MARK}[/bold green] {escape(message)}")

    def fail(self, message: str):
        """Print a red cross followed by an unstyled message on the same line."""
        self._console.print(f"[bold red]{CROSS_MARK}[/bold red] {escape(message)}")

    def list(self, items: list):
        """Print a list of items with bullet points."""
        for item in items:
            self._console.print(f"🔹[bold]{escape(item)}[/bold]")

    def table(self, table: Table) -> None:
        """Render a Rich Table to the console."""
        self._console.print(table)

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


print_console = PrintConsole()
