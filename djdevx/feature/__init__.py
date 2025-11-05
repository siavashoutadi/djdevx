import typer

from .pwa import app as pwa
from .css import app as css
from .tailwind_theme import app as theme

app = typer.Typer(no_args_is_help=True)

app.add_typer(pwa)
app.add_typer(css, name="css", help="Manage css frameworks")
app.add_typer(theme, name="tailwind-theme", help="Manage tailwind theme")
