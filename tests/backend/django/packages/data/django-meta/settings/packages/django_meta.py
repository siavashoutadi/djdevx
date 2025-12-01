from settings import INSTALLED_APPS

# Add django-meta to INSTALLED_APPS
INSTALLED_APPS += [
    "meta",
]

# Protocol and Domain Configuration
# These are required for generating absolute URLs for meta tags
META_SITE_PROTOCOL = "https"
META_SITE_DOMAIN = "example.com"

# Site Information
META_SITE_NAME = "Test Site"
META_SITE_TYPE = "website"

# Default Keywords
META_INCLUDE_KEYWORDS = []  # Extra keywords to include in every view
META_DEFAULT_KEYWORDS = []  # Default keywords when none specified

# Default image for social media sharing (must be absolute URL)
META_DEFAULT_IMAGE = "https://example.com/image.jpg"

# Enable/Disable Meta Tag Types
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMAORG_PROPERTIES = True
META_USE_TITLE_TAG = True

# Use Django Sites Framework (optional)
META_USE_SITES = False

# Facebook/OpenGraph Configuration
META_FB_APPID = "123456"
META_FB_PAGES = "789012"
META_FB_PUBLISHER = "https://facebook.com/testpage"
# Twitter Configuration
META_TWITTER_SITE = "@testsite"
META_TWITTER_AUTHOR = "@testauthor"
META_TWITTER_TYPE = "summary_large_image"
