import typer

from typing import Annotated
from django.contrib.auth import get_user_model
from django_typer.management import TyperCommand, command

from users.factories import UserFactory


class Command(TyperCommand):
    """
    Manage users
    """

    @command()
    def seed(
        self,
        count: Annotated[int, typer.Option(help="The number of users to create")] = 5,
    ):
        """
        Seed users
        """
        typer.echo(f"Creating {count} users ...")
        UserFactory.create_batch(count)
        typer.echo(f"{count} users are created.")

    @command()
    def superuser(self):
        """
        Create admin user
        """
        typer.echo("Creating super user ...")
        UserFactory.create_superuser()
        typer.echo("Super user is created.")

    @command()
    def clean(
        self,
        exclude_user: Annotated[list[str], typer.Option()] = [],
    ):
        """
        Delete all users
        """
        typer.echo("Deleting all users ...")
        get_user_model().objects.exclude(username__in=exclude_user).delete()
        typer.echo("All users are deleted.")
