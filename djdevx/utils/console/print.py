import difflib
from typing import Any

from rich.console import Console as RichConsole
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

CHECK_MARK = "\u2713"
CROSS_MARK = "\u2717"
ELLIPSIS = "\u2026"


class Markup(str):
    """String containing intentional Rich markup. Won't be escaped by TableBuilder."""

    pass


GREEN_CHECK_MARK = Markup(f"[bold green]{CHECK_MARK}[/bold green]")
RED_CROSS_MARK = Markup(f"[bold red]{CROSS_MARK}[/bold red]")
YELLOW_CHECKMARK = Markup(f"[bold yellow]{CHECK_MARK}[/bold yellow]")


class TableBuilder:
    """Wrapper around a Rich Table with auto-escaping and context manager support."""

    def __init__(self, console: RichConsole, rich_table: Table):
        self._console = console
        self._table = rich_table

    def add_row(self, *cells: Any) -> None:
        """Add a row, auto-escaping plain strings."""
        escaped = []
        for cell in cells:
            if isinstance(cell, str) and not isinstance(cell, Markup):
                escaped.append(escape(cell))
            else:
                escaped.append(cell)
        self._table.add_row(*escaped)

    def render(self) -> None:
        """Render the table to the console."""
        self._console.print(self._table)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.render()


class NestedStep:
    """A step that holds indented ``✓`` sub-actions and closes with a ``☑`` line."""

    INDENT = "  "

    def __init__(
        self, print_console: "PrintConsole", title: str, done: str | None = None
    ) -> None:
        self._pc = print_console
        self.title = title
        self.done_message = done or f"{title} done"
        print_console.step(title)

    def ok(self, message: str) -> None:
        """Print an indented completed sub-action (``✓ message``)."""
        self._pc._console.print(
            f"{self.INDENT}[bold green]{CHECK_MARK}[/bold green] {escape(message)}"
        )

    def fail(self, message: str) -> None:
        """Print an indented failed sub-action (``✗ message``)."""
        self._pc._console.print(
            f"{self.INDENT}[bold red]{CROSS_MARK}[/bold red] {escape(message)}"
        )

    def warning(self, message: str) -> None:
        """Print an indented warning child line (``⚠ message``)."""
        self._pc._console.print(
            f"{self.INDENT}[bold yellow]⚠[/bold yellow] {escape(message)}"
        )

    def info(self, message: str) -> None:
        """Print an indented plain child line (e.g. a footnote)."""
        self._pc._console.print(f"{self.INDENT}{escape(message)}")

    def done(self) -> None:
        """Close the step by printing the ``☑ <done>`` line."""
        self._pc.step_done(self.done_message)

    def __enter__(self) -> "NestedStep":
        return self

    def __exit__(self, *exc) -> None:
        self.done()


class PrintConsole:
    """Styled output printer for djdevx messages."""

    def step_group(self, title: str, done: str | None = None) -> NestedStep:
        """Create a (possibly nested) step with indented ``✓`` sub-actions."""
        return NestedStep(self, title, done)

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

    def section(self, title: str) -> None:
        """Print a bold cyan section header."""
        self._console.print(f"[bold cyan]{escape(title)}[/bold cyan]")

    def rule(self, style: str = "bright_black") -> None:
        """Print a horizontal separator line to split sections."""
        self._console.print(Rule(style=style))

    def link(self, text: str, url: str) -> None:
        """Print a clickable Rich hyperlink."""
        self._console.print(f"[link={url}]{escape(text)}[/link]")

    def table(
        self,
        title: str,
        columns: list[tuple[str, dict[str, Any]]],
        **table_kwargs,
    ) -> TableBuilder:
        """Create a styled table. Use as a context manager for auto-rendering."""
        rich_table = Table(
            title=title,
            title_style="bold cyan",
            header_style="bold",
            border_style="bright_black",
            **table_kwargs,
        )
        for name, options in columns:
            rich_table.add_column(name, **options)
        return TableBuilder(self._console, rich_table)

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
