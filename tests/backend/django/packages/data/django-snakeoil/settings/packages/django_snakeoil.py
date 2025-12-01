from settings import INSTALLED_APPS

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
        {"name": "description", "content": "Test site description"},
        {"property": "og:description", "content": "Test site description"},
        {"name": "twitter:description", "content": "Test site description"},
        {"property": "og:title", "content": "Test Site"},
        {"property": "og:site_name", "content": "Test Site"},
        {"name": "twitter:title", "content": "Test Site"},
        {"name": "keywords", "content": "test, django, seo"},
        {"name": "author", "content": "Test Author"},
        {"property": "og:type", "content": "website"},
        {"property": "og:url", "content": "https://example.com"},
        {"name": "twitter:url", "content": "https://example.com"},
        {"name": "twitter:domain", "content": "example.com"},
        {"property": "og:locale", "content": "en_US"},
        {"property": "og:image", "content": "https://example.com/image.jpg"},
        {"name": "twitter:image", "content": "https://example.com/image.jpg"},
        {"name": "twitter:site", "content": "@testsite"},
        {"name": "twitter:card", "content": "summary_large_image"},
    ]
}
