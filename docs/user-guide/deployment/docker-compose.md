# Docker Compose

Generate Docker Compose manifests with Traefik reverse-proxy:

```bash
ddx deployment docker-compose generate --domain example.com --traefik-email admin@example.com
```

Options:

| Option | Description |
|--------|-------------|
| `--domain` | Domain name for the deployment |
| `--traefik-email` | Email for Let's Encrypt certificates |
| `--cloudflare-token` | CF_DNS_API_TOKEN for DNS challenge (optional — skips to TLS challenge) |
| `-o, --output` | Output directory (default: `deployment/docker-compose/`) |

If omitted, required values are prompted interactively.

## Generated Layout

```
deployment/docker-compose/
├── traefik/
│   ├── .env                    # TRAEFIK_EMAIL, CF_DNS_API_TOKEN
│   └── docker-compose.yml      # Traefik reverse-proxy service
└── app/
    ├── .env                    # Production config vars (copied from .env.prod + DOMAIN)
    ├── .secrets/               # Secret files (one per secret)
    ├── docker-compose.base.yml # Auto-generated service definition
    └── docker-compose.prod.yml # Custom overlay (edit for your deployment)
```

## File Lifecycle

- **`.env` files** — regenerated on each `generate` run. Shows a diff if changed.
- **`traefik/.env`** — written once; kept if it already exists.
- **`docker-compose.base.yml`** — always regenerated (do not edit).
- **`docker-compose.prod.yml`** — created once, never overwritten. Edit to
  customise image, replicas, volumes, etc.

## Using the Generated Manifests

```bash
# Start Traefik (reverse-proxy, one-time):
docker compose -f deployment/docker-compose/traefik/docker-compose.yml up -d

# Build and deploy your app:
docker compose \
  -f deployment/docker-compose/app/docker-compose.base.yml \
  -f deployment/docker-compose/app/docker-compose.prod.yml \
  up -d
```

## Verification

Before deploying, verify all manifests, secrets, and configs are in place:

```bash
ddx deployment docker-compose verify
```

Checks:

- Manifest files exist (`docker-compose.base.yml`, `docker-compose.prod.yml`)
- Secret files exist (or have resolvable values)
- Config variables are set
- No drift between generated files and expected content
- `traefik/.env` has `TRAEFIK_EMAIL`
- `app/.env` has a valid `DOMAIN`

A healthy output looks like:

```
 ✓  app/docker-compose.base.yml
 ✓  app/docker-compose.prod.yml
 ✓  DB_PASSWORD  (.secrets/DB_PASSWORD)
 ✓  SECRET_KEY   (.secrets/SECRET_KEY)
 ✓  DEBUG        (hardcoded to false)
 ✓  DATABASE_URL (resolved)
 ✓  traefik/.env (current)
All checks passed.
```

## Related

- [Deployment Overview](../deployment.md)
