# Content Security Policy

Generated projects ship with Django's built-in Content Security Policy (CSP)
support enabled. The `django.middleware.csp.ContentSecurityPolicyMiddleware`
middleware and the `django.template.context_processors.csp` context processor
are always present — harmless when no policy is configured, active as soon as
one is.

## Settings

Policies are defined in `settings/django/csp.py` via the `CspSettings`
`AppBaseSettings` subclass, so they follow the same env-driven rules as every
other setting:

| Setting | Env var | Description |
| ------- | ------- | ----------- |
| `csp_default_src` … `csp_upgrade_insecure_requests` | `CSP_DEFAULT_SRC` … `CSP_UPGRADE_INSECURE_REQUESTS` | Per-directive values. Space-separated sources for list directives; `true`/`false` for flags. Strict defaults apply; override by setting a var. |
| `secure_csp_report_only` | `SECURE_CSP_REPORT_ONLY` | Report-only policy — JSON object; logs violations without blocking. |

## Dev vs Production Defaults

Both dev and production default to a strict enforced policy. Dev additionally
permits `data:` images and `ws:`/`wss:` connections (live reload); production
drops those leniencies and adds `upgrade-insecure-requests`.

## Directives

| Directive | Dev | Prod | What it controls |
| -------- | --- | ---- | ---------------- |
| `default-src` | `'self'` | `'self'` | Fallback for every directive not explicitly listed. `'self'` = same origin only. |
| `script-src` | `'self'` | `'self'` | Where JavaScript can load/run. `'self'` blocks inline `<script>` and `eval()` unless a nonce/hash is used. |
| `style-src` | `'self'` | `'self'` | Where CSS can load. `'self'` blocks inline `style=""` and `<style>` unless nonce/hash allowed. |
| `img-src` | `'self' data:` | `'self'` | Where images may load. `data:` (dev only) allows inline `data:`-URI images. |
| `font-src` | `'self'` | `'self'` | Where web fonts may load (e.g. Google Fonts needs its origin added). |
| `connect-src` | `'self' ws: wss:` | `'self'` | Origins for `fetch()`, XHR, WebSockets, EventSource. `ws:`/`wss:` (dev only) enable live reload. |
| `media-src` | `'self'` | `'self'` | Where `<audio>`/`<video>` may load from. |
| `object-src` | `'none'` | `'none'` | Plugin objects (`<object>`, `<embed>`). `'none'` disables them entirely — blocks a common attack vector. |
| `base-uri` | `'self'` | `'self'` | Allowed `<base>` URLs. Prevents base-tag injection that redirects relative URLs. |
| `frame-ancestors` | `'self'` | `'self'` | Who may embed **our** page in an `<iframe>` (defense against clickjacking). |
| `frame-src` | `'self'` | `'self'` | What **we** may embed via `<iframe>`/`<frame>` (e.g. YouTube embeds need `youtube.com`). |
| `form-action` | `'self'` | `'self'` | Where `<form>` submissions may be sent. Blocks form-abuse to external origins. |
| `upgrade-insecure-requests` | — | ✓ | Flag: browser upgrades all `http://` requests to `https://`. Requires the site served over HTTPS. |

Notes:

- `default-src 'self'` is the safety net — any unlisted directive inherits it,
  so nothing falls back to lenient browser defaults.
- `'self'` for `script-src`/`style-src` means inline code is blocked; add
  `CSP.NONCE` (see below) to allow specific inline elements.
- CDN/third-party resources (fonts, analytics, embeds) are blocked until their
  origins are added to the relevant directive — the deliberate strict-prod
  tradeoff.
- `upgrade-insecure-requests` is ignored in report-only mode per spec.

## Overriding the Policy

Each directive is a `CSP_<DIRECTIVE>` variable (hyphens become underscores) with
a strict default. Setting a variable *replaces* that directive entirely —
include `'self'` if you want to keep it:

```bash
CSP_SCRIPT_SRC="'self' https://cdn.example.com"
CSP_IMG_SRC="'self' data: https://images.example.com"
CSP_CONNECT_SRC="'self' https://api.example.com wss://ws.example.com"
CSP_UPGRADE_INSECURE_REQUESTS=true
```

Directives not in the strict base are omitted from the policy until set — e.g.
`CSP_WORKER_SRC="'self' https://cdn.example.com"` adds a `worker-src` directive.

For a report-only policy (logs violations without blocking), set a JSON object:

```bash
SECURE_CSP_REPORT_ONLY={"default-src":["'self'"],"object-src":["'none'"]}
```

In code, use the `CSP` constants from `django.utils.csp` rather than raw strings
for field defaults or overriding `SECURE_CSP`:

```python
from django.utils.csp import CSP

csp_default_src = CSP.SELF
```

The full list of configurable directives (matching the `CSPDirective` type in
`settings/django/csp.py`): `default-src`, `script-src`, `script-src-elem`,
`script-src-attr`, `style-src`, `style-src-elem`, `style-src-attr`, `img-src`,
`font-src`, `connect-src`, `media-src`, `object-src`, `child-src`, `frame-src`,
`worker-src`, `fenced-frame-src`, `manifest-src`, `prefetch-src`, `base-uri`,
`sandbox`, `form-action`, `frame-ancestors`, `report-to`,
`require-trusted-types-for`, `trusted-types`, `upgrade-insecure-requests`.

## Nonces

Include `CSP.NONCE` in `script-src` or `style-src` to allow specific inline
elements without `'unsafe-inline'`. The middleware swaps in a per-request nonce
and exposes it to templates through the `csp` context processor:

```html
<script nonce="{{ csp_nonce }}">…</script>
```

For external `<script src>` / `<link rel="stylesheet">` tags and `Media`
objects, use the `csp_nonce_attr` template tag (Django 6.1+):

```html
<script src="/path/to/script.js" {% csp_nonce_attr %}></script>
```

The Django admin and other built-in templates apply nonces automatically. Do
not full-page-cache responses that render `csp_nonce` or `csp_nonce_attr` —
reused nonces defeat the mechanism.

## See Also

- [Managing Settings](managing-settings.md) — how settings are organized and
  configured in generated projects.
