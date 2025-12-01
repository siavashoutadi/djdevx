FROM python:3.14-slim AS base

FROM base AS static_builds

WORKDIR /app

RUN apt-get update && apt-get install gettext -y

ADD . /app

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    mkdir /app/locale/ && \
    uv run manage.py collectstatic --noinput && \
    uv run manage.py compilemessages

FROM base AS builder

WORKDIR /app

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-editable --no-dev

FROM base AS source

WORKDIR /app

COPY . /app/
RUN rm -rf staticfiles/src docker pyproject.toml uv.lock

FROM base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PATH=/app/.venv/bin/:$PATH

EXPOSE 8000

ARG USERNAME=django
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}

WORKDIR /app

COPY --from=source --chown=${USERNAME}:${USERNAME} /app /app/
COPY --from=builder --chown=${USERNAME}:${USERNAME} /app/.venv/ /app/.venv
COPY --from=static_builds --chown=${USERNAME}:${USERNAME} /app/staticfiles/ /app/staticfiles/
COPY --from=static_builds --chown=${USERNAME}:${USERNAME} /app/locale /app/locale/
COPY --chown=${USERNAME}:${USERNAME} docker/entrypoint.sh /app/

RUN chmod +x /app/entrypoint.sh

USER ${USERNAME}

ENTRYPOINT ["/bin/bash", "-euo", "pipefail", "/app/entrypoint.sh"]
