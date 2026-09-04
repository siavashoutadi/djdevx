"""Single BaseProvider for all installable domains.

Historically each domain (packages, features, frameworks, database, cache)
defined its own near-identical base class that differed only by ``section``
and its ``get_registry()`` target. This module consolidates them into one
:class:`Provider` parameterized by an :class:`~djdevx.installable.models.InstallableKind`,
plus a :class:`CSSFrameworkProviderMixin` that carries the CSS/JS download and
base-template-injection behavior previously living only in ``BaseFramework``.

The per-domain ``_base.py``/``_registry.py`` modules remain as thin aliases
over this class (and are removed in a later phase once importers are migrated),
so existing provider payloads and tests keep working unchanged.
"""

from typing import ClassVar

from pydantic import model_validator

from .utils.console.print import print_console
from .installable.lifecycle import Installable
from .installable.models import InstallableKind
from .utils.tracking import Section

# Re-export the five canonical kinds so callers don't need a separate import.
# (Mirrors the InstallableKind constants in utils/installable/types.py.)
PACKAGE_KIND = InstallableKind("package", Section.PACKAGES)
FEATURE_KIND = InstallableKind("feature", Section.FEATURES)
FRAMEWORK_KIND = InstallableKind("framework", Section.FRAMEWORKS)
DATABASE_KIND = InstallableKind("database", Section.DATABASE)
CACHE_KIND = InstallableKind("cache", Section.CACHE)


class Provider(Installable):
    """Single base class for every installable provider.

    Subclasses declare ``kind`` (an :class:`InstallableKind`). ``section`` is
    derived at both the class level (so ``get_section(cls)`` returns the right
    value) and the instance level (so ``self.section`` is correct). The
    ``model_validator`` handles instance-level derivation; ``__init_subclass__``
    patches the pydantic field default so ``get_section(cls)`` and CLI
    introspection get the right section too.
    """

    kind: ClassVar[InstallableKind]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        kind = cls.__dict__.get("kind")
        if kind is not None:
            section_field = cls.model_fields.get("section")
            if section_field is not None:
                section_field.default = kind.section

    @model_validator(mode="after")
    def _apply_kind_section(self):
        kind = type(self).kind
        if kind is not None:
            self.section = kind.section
        return self

    @classmethod
    def get_registry(cls):
        from .installable.registry import REGISTRIES

        return REGISTRIES[cls.kind.name]


class CSSFrameworkProviderMixin:
    """CSS/JS framework behavior: download vendor assets, edit the base template.

    Formerly woven into ``BaseFramework``. Only framework providers subclass
    this; other domains inherit plain :class:`Provider`.

    The CSS/JS data fields (``css_url``, ``css_filename``, ``js_url``,
    ``js_filename``, ``js_module``) live on the ``CSSFramework`` model in
    ``frameworks/_base.py`` rather than here: declaring them as plain class
    attributes on a non-pydantic mixin would make pydantic warn when a
    framework subclass redeclares them as fields. ``_base_template_path`` also
    lives on ``BaseFramework`` so every framework (CSS or not) can resolve the
    base template.
    """

    @property
    def _style_tag(self) -> str:
        return f'<link rel="stylesheet" href="{{% static \'css/vendor/{self.css_filename}\' %}}">'

    @property
    def _script_tag(self) -> str:
        tm = ' type="module"' if self.js_module else ""
        return f"<script{tm} src=\"{{% static 'js/vendor/{self.js_filename}' %}}\"></script>"

    def _download(self, url: str, dest) -> None:
        import urllib.request
        from pathlib import Path

        if not isinstance(dest, Path):
            dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, dest)
        except (OSError, ValueError) as exc:
            print_console.warning(
                f"Could not download {url} ({exc}); wrote placeholder instead."
            )
            dest.write_text("/* placeholder */\n")

    def after_copy_templates(self, step=None) -> None:
        self._install_framework()

    def before_pixi_remove(self, step=None) -> None:
        super().before_pixi_remove(step=step)
        self._uninstall_framework()

    def _install_framework(self) -> None:
        if self.css_url and self.css_filename:
            dest = self.structure.static_css_dir / "vendor" / self.css_filename
            if not dest.exists():
                self._download(self.css_url, dest)

        if self.js_url and self.js_filename:
            dest = self.structure.static_js_dir / "vendor" / self.js_filename
            if not dest.exists():
                self._download(self.js_url, dest)

        self._modify_base_template(install=True)

    def _uninstall_framework(self) -> None:
        self._modify_base_template(install=False)

        if self.css_filename:
            (self.structure.static_css_dir / "vendor" / self.css_filename).unlink(
                missing_ok=True
            )
        if self.js_filename:
            (self.structure.static_js_dir / "vendor" / self.js_filename).unlink(
                missing_ok=True
            )

    def _modify_base_template(self, install: bool = True) -> None:
        import re

        path = self._base_template_path
        if not path.exists():
            return
        content = path.read_text()

        if install:
            if self.css_filename and self.css_filename not in content:
                content = content.replace(
                    "</head>", f"    {self._style_tag}\n  </head>"
                )
            if self.js_filename and self.js_filename not in content:
                content = content.replace(
                    "</body>", f"    {self._script_tag}\n  </body>"
                )
        else:
            if self.css_filename:
                content = re.sub(
                    r"\s*" + re.escape(self._style_tag) + r"\s*\n?",
                    "",
                    content,
                )
            if self.js_filename:
                content = re.sub(
                    r"\s*" + re.escape(self._script_tag) + r"\s*\n?",
                    "",
                    content,
                )

        path.write_text(content)
