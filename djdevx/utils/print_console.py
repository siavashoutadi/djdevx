import difflib
from rich.console import Console
from rich.text import Text

console = Console()


def print_step(line: str):
    console.print(f"[bold cyan]{line}[/bold cyan]")


def print_success(line: str):
    console.print(f"[bold green]{line}[/bold green]")


def print_error(line: str):
    console.print(f"[bold red]{line}[/bold red]")


def print_info(line: str):
    console.print(f"{line}")


def print_warning(line: str):
    console.print(f"[bold yellow]{line}[/bold yellow]")


def print_list(items: list):
    for item in items:
        console.print(f"🔹[bold]{item}[/bold]")


def print_diff(old: str, new: str, title_old="(current)", title_new="(new)"):
    console.print(f"[bold cyan]Diff: {title_old} -> {title_new}[/bold cyan]")

    for line in difflib.ndiff(
        old.splitlines(keepends=False),
        new.splitlines(keepends=False),
    ):
        prefix, body = line[:2], line[2:]
        if prefix == "- ":
            console.print(Text("- " + body, style="on red"))
        elif prefix == "+ ":
            console.print(Text("+ " + body, style="on green"))
        elif prefix == "  ":
            console.print("  " + body)
