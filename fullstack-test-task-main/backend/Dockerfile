FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

COPY .env ./
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/src ./src

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

RUN uv sync
