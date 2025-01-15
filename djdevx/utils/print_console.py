from rich.console import Console

console = Console()


def print_step(line: str):
    console.print(f"[bold cyan]{line}[/bold cyan]")


def print_success(line: str):
    console.print(f"\n[bold green]{line}[/bold green]\n")


def print_error(line: str):
    console.print(f"\n[bold red]{line}[/bold red]\n")


def print_info(line: str):
    console.print(f"{line}")


def print_warning(line: str):
    console.print(f"\n[bold yellow]{line}[/bold yellow]\n")
