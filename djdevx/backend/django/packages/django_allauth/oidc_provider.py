import typer
import shutil
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager
from .....utils.djdevx_config import DjdevxConfig


app = typer.Typer(no_args_is_help=True)


def remove_env_variable_from_file(file_path: Path, key: str) -> None:
    """Remove an environment variable from a .env file, handling multiline values."""
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith(f"{key}="):
            i += 1
            while i < len(lines):
                current_line = lines[i]
                if "-----END" in current_line:
                    i += 1
                    if i < len(lines) and lines[i].strip() == "'":
                        i += 1
                    break
                i += 1
        else:
            new_lines.append(line)
            i += 1

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


@app.command()
def install():
    """
    Install and configure django-allauth OIDC provider.

    Note: Requires django-allauth account to be installed first.
    Configure environment variables using the 'env' command.
    """
    pm = DjangoProjectManager()

    console.step("Checking if django-allauth account is installed ...")

    account_settings_path = Path.joinpath(
        pm.packages_settings_path, "django_allauth_account.py"
    )

    if not account_settings_path.exists():
        console.error(
            "django-allauth account functionality is not configured. Please install it first."
        )
        console.info("\n> ddx backend django packages django-allauth account install")
        raise typer.Exit(1)

    console.step("Installing django-allauth OIDC provider ...")

    uv = UvRunner()
    uv.add_package("django-allauth[idp-oidc]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_allauth"
        / "oidc_provider"
    )

    pm.copy_templates(
        source_dir=source_dir,
        template_context={},
    )

    env()

    console.success("django-allauth OIDC provider is installed successfully.")


@app.command()
def remove():
    """
    Remove OIDC provider configuration.

    Note: This removes OIDC configuration but keeps django-allauth[idp-oidc]
    package installed. To completely remove django-allauth, use the account remove command.
    """
    pm = DjangoProjectManager()

    console.step("Removing django-allauth OIDC provider configuration ...")

    # Remove OIDC provider settings file
    oidc_settings_path = Path.joinpath(
        pm.packages_settings_path, "django_allauth_oidc_provider.py"
    )
    oidc_settings_path.unlink(missing_ok=True)

    oidc_urls_path = Path.joinpath(
        pm.packages_urls_path, "django_allauth_oidc_provider.py"
    )
    oidc_urls_path.unlink(missing_ok=True)

    # Remove OIDC provider templates
    oidc_templates_path = Path.joinpath(
        pm.project_path, "authentication", "templates", "idp", "oidc"
    )
    shutil.rmtree(oidc_templates_path, ignore_errors=True)

    # Remove OIDC provider management commands
    oidc_management_path = Path.joinpath(
        pm.project_path, "authentication", "management", "commands", "pkce_oauth.py"
    )
    oidc_management_path.unlink(missing_ok=True)

    # Remove management commands __init__.py if it exists and is empty
    management_init_path = Path.joinpath(
        pm.project_path, "authentication", "management", "commands", "__init__.py"
    )
    management_init_path.unlink(missing_ok=True)

    djdevx_config = DjdevxConfig()
    devcontainer_env_path = djdevx_config.devcontainer_env_devcontainer_path
    remove_env_variable_from_file(devcontainer_env_path, "IDP_OIDC_PRIVATE_KEY")

    console.success(
        "django-allauth OIDC provider configuration is removed successfully."
    )
    console.info(
        "Note: django-allauth[idp-oidc] package remains installed. Use 'ddx backend django packages django-allauth account remove' to remove the entire package."
    )


@app.command()
def env():
    """
    Configure environment variables for OIDC provider.

    Auto-generates a private key for signing ID tokens.
    """

    console.step("Configuring environment variables for OIDC provider ...")
    console.step("Generating RSA 2048-bit private key ...")

    private_key_obj = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    # Serialize to PEM format
    private_key = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    console.success("Private key generated successfully.")

    pm = DjangoProjectManager()
    pm.add_env_variable(key="IDP_OIDC_PRIVATE_KEY", value=f"'{private_key}'")

    console.success("OIDC provider environment variables configured successfully.")
    console.info("Private key has been saved to .env as IDP_OIDC_PRIVATE_KEY")
