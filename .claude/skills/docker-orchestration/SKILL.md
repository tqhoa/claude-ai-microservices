---
name: docker-orchestration
description: Docker Compose orchestration cho microservices bao gồm multi-stage builds, health checks, networking, và volume management. Sử dụng khi cần Docker setup, docker-compose config, hoặc container optimization.
---

# Kỹ Năng Docker Orchestration

Orchestration microservices với Docker Compose.

---

## Cấu Trúc Docker Files

```
.
├── docker-compose.yml          # Base config (services, networks, volumes)
├── docker-compose.dev.yml      # Override: hot reload, debug ports, volumes
├── docker-compose.prod.yml     # Override: build optimization, replicas
├── docker-compose.test.yml     # Override: test database, test runners
├── .env                        # Shared environment variables
├── .env.example                # Template cho team
├── api_gateway/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── nginx.dev.conf
├── backend/
│   └── Dockerfile              # Multi-stage: builder → development → production
└── frontend/
    └── Dockerfile              # Multi-stage: builder → development → production(nginx)
```

---

## Backend Dockerfile (Multi-Target)

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Dependencies stage
FROM base AS deps
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Development target
FROM base AS development
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production target
FROM base AS production
RUN groupadd -r app && useradd -r -g app app
COPY --from=deps /app/.venv .venv
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD [".venv/bin/python", "-c", "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"]
CMD [".venv/bin/gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Frontend Dockerfile (Multi-Target)

```dockerfile
# frontend/Dockerfile
FROM node:22-alpine AS base
RUN corepack enable
WORKDIR /app

# Dependencies
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Development target
FROM base AS development
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]

# Build
FROM deps AS builder
COPY . .
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN pnpm build

# Production target (Nginx serve static)
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

## API Gateway Dockerfile

```dockerfile
# api_gateway/Dockerfile
FROM nginx:1.27-alpine
RUN addgroup -g 1001 -S app && adduser -S -D -H -u 1001 -h /tmp -s /sbin/nologin -G app app
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
EXPOSE 80 443
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/health || exit 1
```

---

## Docker Compose Patterns

```yaml
# docker-compose.yml
services:
  gateway:
    build: ./api_gateway
    ports: ["${GATEWAY_PORT:-80}:80"]
    depends_on:
      backend: { condition: service_healthy }
    networks: [frontend-net, backend-net]
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      target: production
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    networks: [backend-net]
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      target: production
    networks: [frontend-net]
    restart: unless-stopped

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-appdb}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]
    networks: [backend-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    networks: [backend-net]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5
    restart: unless-stopped

networks:
  frontend-net:
  backend-net:

volumes:
  pgdata:
```

---

## Lệnh Hàng Ngày

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Chạy migration
docker compose exec backend alembic upgrade head

# Xem log
docker compose logs -f --tail=100 backend gateway

# Scale backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3

# Dọn dẹp
docker compose down -v --rmi local
```

## Bảng Kiểm Tra
- [ ] Multi-stage builds cho tất cả services
- [ ] Health checks cho tất cả services
- [ ] Network isolation (frontend-net, backend-net)
- [ ] Volume cho persistent data
- [ ] .env.example committed, .env trong .gitignore
- [ ] depends_on với condition: service_healthy
- [ ] restart: unless-stopped
- [ ] Non-root user trong production images
