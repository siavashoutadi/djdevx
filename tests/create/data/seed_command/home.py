import typer

from typing import Annotated
from django_typer.management import TyperCommand, command

from home.factories import PostFactory
from home.models import Post


class Command(TyperCommand):
    """Seed and clean the home app models."""

    @command()
    def seed_post(
        self,
        count: Annotated[int, typer.Option(help="Number of posts to create")] = 5,
    ):
        """Create posts via factory-boy."""
        typer.echo(f"Creating {count} posts ...")
        PostFactory.create_batch(count)
        typer.echo(f"{count} posts created.")

    @command()
    def clean_post(self):
        """Delete all posts."""
        typer.echo("Deleting all posts ...")
        Post.objects.all().delete()
        typer.echo("All posts deleted.")
