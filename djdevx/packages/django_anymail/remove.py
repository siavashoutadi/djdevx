import subprocess

from pathlib import Path
from ...utils.print_console import print_step, print_success
from ...utils.project_files import get_packages_settings_path, remove_env_varibles


def remove_package():
    """
    Remove django-anymail package
    """
    print_step("Removing django-anymail package ...")
    subprocess.check_call(["uv", "remove", "django-anymail"])

    settings_url = Path.joinpath(get_packages_settings_path(), "django_anymail.py")
    settings_url.unlink(missing_ok=True)

    print_success("django-anymail package is removed successfully.")

    remove_env_varibles("ANYMAIL_SES_ACCESS_KEY")
    remove_env_varibles("ANYMAIL_SES_SECRET_KEY")
    remove_env_varibles("ANYMAIL_SES_REGION_NAME")
    remove_env_varibles("ANYMAIL_BREVO_API_KEY")
    remove_env_varibles("ANYMAIL_MAILGUN_API_KEY")
    remove_env_varibles("ANYMAIL_MAILJET_API_KEY")
    remove_env_varibles("ANYMAIL_MAILJET_SECRET_KEY")
    remove_env_varibles("ANYMAIL_RESEND_API_KEY")
