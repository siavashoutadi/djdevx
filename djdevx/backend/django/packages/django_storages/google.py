from pathlib import Path

from .._base import BasePackage, EnvParam


class GoogleStoragePackage(BasePackage):
    name = "django-storages Google Cloud Storage"
    packages = ["django-storages[google]"]

    env_params = [
        EnvParam(
            name="credentials_file_path",
            env_key="STORAGES_GOOGLE_CREDENTIALS",
            type_=Path,
            default=None,
            help="The path to the google credential file",
            prompt="Please enter the path to the google credential file",
        ),
        EnvParam(
            name="bucket_name",
            env_key="STORAGES_GOOGLE_BUCKET_NAME",
            help="The Google bucket name to store the files in",
            prompt="Please enter the Google bucket name to store the files in",
        ),
    ]


_pkg = GoogleStoragePackage(__file__)
app = _pkg.app
