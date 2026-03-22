FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Development target
FROM base AS development
RUN pip install uv
COPY pyproject.toml ./
RUN uv sync --frozen || uv sync
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Dependencies for production
FROM base AS deps
RUN pip install uv
COPY pyproject.toml ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Production target
FROM base AS production
RUN groupadd -r app && useradd -r -g app app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=deps /app/.venv .venv
COPY app/ app/
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
