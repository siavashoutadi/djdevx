"""ddx deployment — generate deployment manifests for various targets.

Currently supported targets:
  * docker-compose   Docker Compose (Traefik + web service)

Future targets:
  * docker-swarm     Docker Swarm stack files
  * k8s/helmfile     Kubernetes via Helmfile
  * k8s/argo         Kubernetes via Argo CD (GitOps)
  * k8s/flux         Kubernetes via Flux (GitOps)
"""

from __future__ import annotations

import typer

from .docker_compose import app as docker_compose_app

app = typer.Typer(
    no_args_is_help=True,
    help="Generate deployment manifests",
)

app.add_typer(
    docker_compose_app,
    name="docker-compose",
    help="Docker Compose: generate manifests + verify",
)
