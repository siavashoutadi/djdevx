from typing import Any, Literal, Optional

from django.utils.csp import CSP

from settings.utils.base_settings import AppBaseSettings

CSPDirective = Literal[
    "default-src",
    "script-src",
    "script-src-elem",
    "script-src-attr",
    "style-src",
    "style-src-elem",
    "style-src-attr",
    "img-src",
    "font-src",
    "connect-src",
    "media-src",
    "object-src",
    "child-src",
    "frame-src",
    "worker-src",
    "fenced-frame-src",
    "manifest-src",
    "prefetch-src",
    "base-uri",
    "sandbox",
    "form-action",
    "frame-ancestors",
    "report-to",
    "require-trusted-types-for",
    "trusted-types",
    "upgrade-insecure-requests",
]

_FIELD_TO_DIRECTIVE: dict[str, CSPDirective] = {
    "csp_default_src": "default-src",
    "csp_script_src": "script-src",
    "csp_script_src_elem": "script-src-elem",
    "csp_script_src_attr": "script-src-attr",
    "csp_style_src": "style-src",
    "csp_style_src_elem": "style-src-elem",
    "csp_style_src_attr": "style-src-attr",
    "csp_img_src": "img-src",
    "csp_font_src": "font-src",
    "csp_connect_src": "connect-src",
    "csp_media_src": "media-src",
    "csp_object_src": "object-src",
    "csp_child_src": "child-src",
    "csp_frame_src": "frame-src",
    "csp_worker_src": "worker-src",
    "csp_fenced_frame_src": "fenced-frame-src",
    "csp_manifest_src": "manifest-src",
    "csp_prefetch_src": "prefetch-src",
    "csp_base_uri": "base-uri",
    "csp_sandbox": "sandbox",
    "csp_form_action": "form-action",
    "csp_frame_ancestors": "frame-ancestors",
    "csp_report_to": "report-to",
    "csp_require_trusted_types_for": "require-trusted-types-for",
    "csp_trusted_types": "trusted-types",
    "csp_upgrade_insecure_requests": "upgrade-insecure-requests",
}


class CspSettings(AppBaseSettings):
    secure_csp_report_only: Optional[dict[str, Any]] = None

    csp_default_src: str = CSP.SELF
    csp_script_src: str = CSP.SELF
    csp_style_src: str = CSP.SELF
    csp_img_src: str = CSP.SELF
    csp_font_src: str = CSP.SELF
    csp_connect_src: str = CSP.SELF
    csp_media_src: str = CSP.SELF
    csp_object_src: str = CSP.NONE
    csp_base_uri: str = CSP.SELF
    csp_frame_ancestors: str = CSP.SELF
    csp_form_action: str = CSP.SELF
    csp_frame_src: str = CSP.SELF

    csp_script_src_elem: Optional[str] = None
    csp_script_src_attr: Optional[str] = None
    csp_style_src_elem: Optional[str] = None
    csp_style_src_attr: Optional[str] = None
    csp_child_src: Optional[str] = None
    csp_worker_src: Optional[str] = None
    csp_fenced_frame_src: Optional[str] = None
    csp_manifest_src: Optional[str] = None
    csp_prefetch_src: Optional[str] = None
    csp_sandbox: Optional[str] = None
    csp_report_to: Optional[str] = None
    csp_require_trusted_types_for: Optional[str] = None
    csp_trusted_types: Optional[str] = None
    csp_upgrade_insecure_requests: Optional[bool] = None

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "csp_img_src": "'self' data:",
            "csp_connect_src": "'self' ws: wss:",
        }

    @classmethod
    def get_prod_defaults(cls) -> dict[str, Any]:
        return {
            "csp_upgrade_insecure_requests": True,
        }


_csp = CspSettings()

SECURE_CSP: dict[CSPDirective, str | bool] = {
    directive: getattr(_csp, field)
    for field, directive in _FIELD_TO_DIRECTIVE.items()
    if getattr(_csp, field) is not None
}

if _csp.secure_csp_report_only:
    SECURE_CSP_REPORT_ONLY = _csp.secure_csp_report_only
