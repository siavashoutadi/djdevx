from ._base import BasePackage, InstallParam


class DjangoMetaPackage(BasePackage):
    name = "django-meta"
    packages = ["django-meta"]

    install_params = [
        InstallParam(
            name="site_protocol",
            default="https",
            help="Protocol for your site URL: 'http' or 'https' (use https for production)",
            prompt="Please enter your site protocol (http/https)",
        ),
        InstallParam(
            name="site_domain",
            help="Your website domain without protocol (e.g., 'example.com' or 'blog.example.com')",
            prompt="Please enter your site domain (e.g., example.com)",
        ),
        InstallParam(
            name="site_name",
            help="Display name of your website (e.g., 'My Awesome Blog')",
            prompt="Please enter your site name",
        ),
        InstallParam(
            name="site_type",
            default="website",
            help="OpenGraph type (website, article, blog, product). See: https://ogp.me/#types",
            prompt="Please enter your site type (website/article/blog/product)",
        ),
        InstallParam(
            name="use_og_properties",
            type_=bool,
            default=True,
            help="Enable OpenGraph meta tags for rich previews on Facebook, LinkedIn, WhatsApp, etc.",
            prompt="Enable OpenGraph properties (Facebook, LinkedIn, WhatsApp)?",
        ),
        InstallParam(
            name="use_twitter_properties",
            type_=bool,
            default=True,
            help="Enable Twitter Card meta tags for rich previews when links are shared on Twitter/X",
            prompt="Enable Twitter Card properties for rich previews on Twitter/X?",
        ),
        InstallParam(
            name="use_schemaorg_properties",
            type_=bool,
            default=True,
            help="Enable Schema.org structured data for better SEO and search engine understanding",
            prompt="Enable Schema.org properties for better SEO?",
        ),
        InstallParam(
            name="use_title_tag",
            type_=bool,
            default=True,
            help="Auto-render <title> tags in templates (disable if you manage titles manually)",
            prompt="Render <title> tag automatically?",
        ),
        InstallParam(
            name="configure_facebook",
            type_=bool,
            default=False,
            help="Configure Facebook-specific settings (App ID, Pages, Publisher).",
            prompt="Do you want to configure Facebook/OpenGraph settings?",
        ),
        InstallParam(
            name="fb_app_id",
            show_if="configure_facebook",
            help="Facebook App ID from https://developers.facebook.com/apps/ (numeric ID)",
            prompt="Enter your Facebook App ID (numeric, e.g., 123456789012345) or leave empty",
            message_before_prompt="\nGet your App ID from: https://developers.facebook.com/apps/",
        ),
        InstallParam(
            name="fb_pages",
            show_if="configure_facebook",
            help="Facebook Page ID for your business page (numeric ID)",
            prompt="Enter your Facebook Page ID (numeric) or leave empty",
            message_before_prompt="\nFind your Page ID at: facebook.com/your-page/about",
        ),
        InstallParam(
            name="fb_publisher",
            show_if="configure_facebook",
            help="Full Facebook Page URL (e.g., 'https://www.facebook.com/YourPageName')",
            prompt="Enter your Facebook Page URL (e.g., https://www.facebook.com/YourPage) or leave empty",
            message_before_prompt="\nUse your full Facebook Page URL",
        ),
        InstallParam(
            name="configure_twitter",
            type_=bool,
            default=False,
            help="Configure Twitter Card settings for rich previews.",
            prompt="Do you want to configure Twitter Card settings?",
        ),
        InstallParam(
            name="twitter_site",
            show_if="configure_twitter",
            help="Your website's Twitter/X handle including @ (e.g., '@YourSite')",
            prompt="Your site's Twitter handle (e.g., @YourSite)",
            message_before_prompt="\nEnter your website's Twitter/X handle",
        ),
        InstallParam(
            name="twitter_author",
            show_if="configure_twitter",
            help="Default author Twitter/X handle with @ (e.g., '@AuthorName')",
            prompt="Default author Twitter handle (e.g., @AuthorName) or leave empty",
            message_before_prompt="\nDefault author handle for content attribution",
        ),
        InstallParam(
            name="twitter_type",
            default="summary_large_image",
            show_if="configure_twitter",
            help="Twitter Card type: 'summary' or 'summary_large_image'",
            prompt="Twitter card type",
            message_before_prompt="\nCard types: 'summary' (small image) or 'summary_large_image' (large image, recommended)",
        ),
        InstallParam(
            name="default_image_url",
            help="Full URL to default share image (1200x630px recommended)",
            prompt="Enter default image URL for social sharing (leave empty to skip)",
        ),
    ]


_pkg = DjangoMetaPackage(__file__)
app = _pkg.app
