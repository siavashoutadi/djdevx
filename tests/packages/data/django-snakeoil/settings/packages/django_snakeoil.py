from settings.django.base import INSTALLED_APPS

# django-snakeoil configuration
# https://django-snakeoil.readthedocs.io/

# Add snakeoil to INSTALLED_APPS for Django template support
INSTALLED_APPS += [
    "snakeoil",
]

# Configure default meta tags for all pages
# Tags are organized by language code. Use "default" for all languages.
# More specific languages (e.g., "en_GB") override less specific ones (e.g., "en")
SNAKEOIL_DEFAULT_TAGS = {
    "default": [
        {"property": "og:type", "content": "website"},
        {"property": "og:image", "static": "images/logo.svg"},
        {"name": "twitter:image", "static": "images/logo.svg"},
        {"name": "twitter:card", "content": "summary_large_image"},
    ]
}
