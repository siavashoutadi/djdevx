import subprocess

from pathlib import Path
from ...utils.print_console import print_step, print_success
from ...utils.project_files import get_packages_settings_path, remove_env_varibles


def remove_package():
    """
    Remove django-storages
    """
    print_step("Removing django-storages package ...")
    subprocess.check_call(["uv", "remove", "django-storages"])

    settings_url = Path.joinpath(get_packages_settings_path(), "django_storages.py")
    settings_url.unlink(missing_ok=True)

    print_success("django-storages is removed successfully.")

    remove_env_varibles(key="STORAGES_S3_ACCESS_KEY")
    remove_env_varibles(key="STORAGES_S3_SECRET_KEY")
    remove_env_varibles(key="STORAGES_S3_REGION_NAME")
    remove_env_varibles(key="STORAGES_S3_BUCKET_NAME")
    remove_env_varibles(key="STORAGES_AZURE_ACCOUNT_KEY")
    remove_env_varibles(key="STORAGES_AZURE_ACCOUNT_NAME")
    remove_env_varibles(key="STORAGES_AZURE_CONTAINER_NAME")
    remove_env_varibles(key="STORAGES_GOOGLE_CREDENTIALS")
    remove_env_varibles(key="STORAGES_GOOGLE_BUCKET_NAME")
