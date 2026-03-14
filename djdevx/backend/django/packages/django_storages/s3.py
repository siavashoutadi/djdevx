from .._base import BasePackage, EnvParam


class S3Package(BasePackage):
    name = "django-storages S3"
    packages = ["django-storages[s3]"]

    env_params = [
        EnvParam(
            name="access_key",
            env_key="STORAGES_S3_ACCESS_KEY",
            help="The AWS access key for authentication",
            prompt="Please enter the AWS access key for authentication",
        ),
        EnvParam(
            name="secret_key",
            env_key="STORAGES_S3_SECRET_KEY",
            help="The AWS Secret key for authentication",
            prompt="Please enter the AWS secret key for authentication",
            hide_input=True,
        ),
        EnvParam(
            name="region_name",
            env_key="STORAGES_S3_REGION_NAME",
            help="The AWS region",
            prompt="Please enter the AWS region",
        ),
        EnvParam(
            name="bucket_name",
            env_key="STORAGES_S3_BUCKET_NAME",
            help="The AWS bucket name to store the files in",
            prompt="Please enter the AWS bucket name to store the files in",
        ),
    ]


_pkg = S3Package(__file__)
app = _pkg.app
