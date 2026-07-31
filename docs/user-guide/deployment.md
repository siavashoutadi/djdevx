# Deployment

djdevx can generate production deployment manifests for your Django project.

## Prerequisites

Before generating manifests, your project must have secrets and config vars
initialized:

```bash
ddx settings secrets init prod
ddx settings configs init prod
```

## Targets

- [Docker Compose](deployment/docker-compose.md) — Traefik reverse-proxy, auto-discovered services
