---
name: ci-cd-pipeline
description: CI/CD pipeline cho microservices với GitHub Actions, change detection, parallel builds, và deployment. Sử dụng khi thiết lập hoặc cải thiện CI/CD.
---

# Kỹ Năng CI/CD Pipeline

GitHub Actions pipeline cho hệ thống microservices với change detection thông minh.

## Nguyên Tắc
- Chỉ build/test service bị thay đổi (change detection)
- Test song song cho mỗi service
- E2E test sau khi tất cả service tests pass
- Docker build chỉ trên nhánh main
- Preview deployment cho Pull Requests

## Workflow Chính

```yaml
name: CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.f.outputs.backend }}
      frontend: ${{ steps.f.outputs.frontend }}
      gateway: ${{ steps.f.outputs.gateway }}
      infra: ${{ steps.f.outputs.infra }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: f
        with:
          filters: |
            backend: ['backend/**']
            frontend: ['frontend/**']
            gateway: ['api_gateway/**']
            infra: ['docker-compose*.yml', '.github/**']

  backend-test:
    needs: detect
    if: needs.detect.outputs.backend == 'true' || needs.detect.outputs.infra == 'true'
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
        options: --health-cmd pg_isready
    defaults:
      run: { working-directory: backend }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install uv && uv sync
      - run: uv run ruff check .
      - run: uv run mypy .
      - run: uv run bandit -r app/
      - run: uv run pytest --cov=app --cov-report=xml
        env: { DATABASE_URL: 'postgresql+asyncpg://postgres:test@localhost:5432/test' }

  frontend-test:
    needs: detect
    if: needs.detect.outputs.frontend == 'true' || needs.detect.outputs.infra == 'true'
    runs-on: ubuntu-latest
    defaults:
      run: { working-directory: frontend }
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: pnpm, cache-dependency-path: frontend/pnpm-lock.yaml }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm type-check
      - run: pnpm test:coverage
      - run: pnpm build

  e2e:
    needs: [backend-test, frontend-test]
    if: always() && !failure()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d --build --wait
      - run: docker compose exec -T backend alembic upgrade head
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
      - run: docker compose down -v
```
