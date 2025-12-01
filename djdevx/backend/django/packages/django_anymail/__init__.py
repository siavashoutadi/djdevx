import typer

from .ses import app as ses_app
from .brevo import app as brevo_app
from .mailgun import app as mailgun_app
from .mailjet import app as mailjet_app
from .resend import app as resend_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    ses_app,
    name="ses",
    help="Manage django-anymail with SES backend",
)

app.add_typer(
    brevo_app,
    name="brevo",
    help="Manage django-anymail with Brevo backend",
)

app.add_typer(
    mailgun_app,
    name="mailgun",
    help="Manage django-anymail with Mailgun backend",
)

app.add_typer(
    mailjet_app,
    name="mailjet",
    help="Manage django-anymail with Mailjet backend",
)

app.add_typer(
    resend_app,
    name="resend",
    help="Manage django-anymail with Resend backend",
)
