"""AnymailPackage — django-anymail with 5 email providers."""

from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ....utils.installable.types import InstallParam, Variant
from .._registry import register


@register
class AnymailPackage(BasePackage):
    name: str = "django-anymail"
    display_name: str = "Django Anymail"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-anymail<16")]
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "ses": Variant(
            name="ses",
            display_name="Amazon SES",
            template_path="ses",
        ),
        "brevo": Variant(
            name="brevo",
            display_name="Brevo",
            template_path="brevo",
        ),
        "mailgun": Variant(
            name="mailgun",
            display_name="Mailgun",
            template_path="mailgun",
            install_params=[
                InstallParam(
                    name="is_europe",
                    type_=bool,
                    default=False,
                    help="Flag to use Europe region for Mailgun",
                ),
            ],
        ),
        "mailjet": Variant(
            name="mailjet",
            display_name="Mailjet",
            template_path="mailjet",
        ),
        "resend": Variant(
            name="resend",
            display_name="Resend",
            template_path="resend",
        ),
    }
