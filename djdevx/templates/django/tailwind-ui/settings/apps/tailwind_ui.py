from settings import INSTALLED_APPS, TEMPLATES

INSTALLED_APPS += [
    "tailwind_ui",
]


for template_engine in TEMPLATES:
    if template_engine["BACKEND"] == "django.template.backends.django.DjangoTemplates":
        if "builtins" not in template_engine["OPTIONS"]:
            template_engine["OPTIONS"]["builtins"] = []
        template_engine["OPTIONS"]["builtins"].append("tailwind_ui.templatetags.twui")
