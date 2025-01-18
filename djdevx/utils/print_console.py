from rich.console import Console

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
