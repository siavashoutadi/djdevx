from settings import INSTALLED_APPS, TEMPLATES


INSTALLED_APPS += [
    "heroicons",
]

for template_engine in TEMPLATES:
    if template_engine["BACKEND"] == "django.template.backends.django.DjangoTemplates":
        if "builtins" not in template_engine["OPTIONS"]:
            template_engine["OPTIONS"]["builtins"] = []
        template_engine["OPTIONS"]["builtins"].append(
            "heroicons.templatetags.heroicons"
        )
