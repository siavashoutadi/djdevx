import subprocess
import shutil

from pathlib import Path
from ...utils.print_console import print_step, print_success
from ...utils.project_files import (
    get_packages_settings_path,
    get_project_path,
    get_url_path,
)


def remove_package():
    """
    Remove django-allauth
    """
    print_step("Removing django-allauth package ...")

    settings_path = Path.joinpath(get_packages_settings_path(), "django_allauth.py")
    settings_path.unlink(missing_ok=True)

    url_path = Path.joinpath(get_url_path(), "django_allauth.py")
    url_path.unlink(missing_ok=True)

    authentication_path = Path.joinpath(get_project_path(), "authentication")
    shutil.rmtree(authentication_path, ignore_errors=True)

    authentication_path = Path.joinpath(get_project_path(), "authentication")
    shutil.rmtree(authentication_path, ignore_errors=True)

    css_path = Path.joinpath(get_project_path(), "static", "css", "vendor", "auth.css")
    css_path.unlink(missing_ok=True)

    subprocess.check_call(["uv", "remove", "django-allauth", "better-profanity"])

    print_success("django-allauth is removed successfully.")
