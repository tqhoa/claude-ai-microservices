# Mẫu Claude Code Cho Kiến Trúc Microservices

Mẫu này cung cấp kiến trúc microservices hoàn chỉnh với 3 service: **API Gateway** (Nginx), **Backend** (FastAPI), và **Frontend** (Vue 3), được tối ưu cho Claude Code với tác nhân và kỹ năng chuyên biệt ở cả cấp hệ thống lẫn từng service.

```
.
├── .claude/                           # Tác nhân & kỹ năng CẤP HỆ THỐNG
│   ├── agents/
│   │   ├── microservices-architect.md  # Kiến trúc sư tổng thể
│   │   ├── devops-engineer.md          # Docker, CI/CD, orchestration
│   │   ├── security-engineer.md        # Bảo mật xuyên services
│   │   ├── code-reviewer.md            # Đánh giá mã cross-service
│   │   └── test-automator.md           # Chiến lược test E2E
│   └── skills/
│       ├── microservices-patterns/     # Giao tiếp, API contract, errors
│       ├── api-gateway-patterns/       # Nginx config hoàn chỉnh
│       ├── docker-orchestration/       # Docker Compose multi-service
│       ├── ci-cd-pipeline/             # GitHub Actions change detection
│       ├── security-patterns/          # Auth flow, CORS, JWT
│       ├── monitoring-observability/   # Logging, tracing, health checks
│       ├── database-patterns/          # Migration, pooling, caching
│       └── testing-strategy/           # Test pyramid, contract, E2E
│
├── api_gateway/                       # SERVICE: Nginx Reverse Proxy
│   ├── .claude/
│   │   ├── agents/gateway-engineer.md
│   │   └── skills/nginx-patterns/
│   ├── CLAUDE.md
│   └── Dockerfile
│
├── backend/                           # SERVICE: FastAPI Async API
│   ├── .claude/
│   │   ├── agents/fastapi-engineer.md
│   │   └── skills/fastapi-patterns/
│   ├── CLAUDE.md
│   └── Dockerfile
│
├── frontend/                          # SERVICE: Vue 3 SPA
│   ├── .claude/
│   │   ├── agents/vuejs-engineer.md
│   │   └── skills/vuejs-patterns/
│   ├── CLAUDE.md
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── CLAUDE.md                          # Hướng dẫn chính
└── README.md
```

## Kiến Trúc

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Frontend   │─────▶│   API Gateway    │─────▶│    Backend      │
│  Vue 3 SPA  │      │  Nginx :80/443   │      │  FastAPI :8000  │
│  TypeScript │      │  CORS, SSL, Rate │      │  Async, JWT     │
│  Pinia      │      │  Limiting, Logs  │      │  SQLAlchemy     │
└─────────────┘      └──────────────────┘      └────────┬────────┘
                                                         │
                                                ┌────────┼────────┐
                                                │        │        │
                                             ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
                                             │ DB  │ │Redis│ │Queue│
                                             │PG17 │ │  7  │ │     │
                                             └─────┘ └─────┘ └─────┘
```

## Tác Nhân (Agents)

### Cấp Hệ Thống (Cross-Service)
| Tác nhân | Model | Mô tả |
|----------|-------|-------|
| `kiến-trúc-sư-microservices` | opus | Thiết kế tổng thể, API contract, auth flow |
| `kỹ-sư-devops` | sonnet | Docker Compose, CI/CD, monitoring |
| `kỹ-sư-bảo-mật` | opus | Auth flow, CORS, SSL, rate limiting |
| `người-đánh-giá-mã` | opus | Đánh giá cross-service, API consistency |
| `tự-động-hóa-test` | sonnet | Test pyramid, E2E, contract testing |

### Cấp Service
| Service | Tác nhân | Mô tả |
|---------|----------|-------|
| API Gateway | `kỹ-sư-gateway` | Nginx config, routing, CORS |
| Backend | `kỹ-sư-fastapi` | FastAPI, SQLAlchemy, JWT |
| Frontend | `kỹ-sư-vuejs` | Vue 3, Pinia, TypeScript |

## Kỹ Năng (Skills)

### Cấp Hệ Thống
- **mẫu-microservices** — API contract, error propagation, service communication
- **mẫu-api-gateway** — Nginx config hoàn chỉnh với CORS, rate limiting, SSL
- **docker-orchestration** — Docker Compose multi-stage, health checks, networking
- **ci-cd-pipeline** — GitHub Actions với change detection thông minh
- **mẫu-bảo-mật** — JWT auth flow, phân bổ trách nhiệm bảo mật
- **giám-sát-quan-sát** — Request ID tracing, structured logging, health checks
- **mẫu-cơ-sở-dữ-liệu** — Migration, connection pooling, Redis caching
- **chiến-lược-kiểm-thử** — Test pyramid, contract testing, E2E

### Cấp Service
Mỗi service có kỹ năng riêng tham chiếu lên kỹ năng gốc.

## Stack Công Nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| API Gateway | Nginx 1.27 |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Frontend | Vue 3, TypeScript, Pinia, TailwindCSS, Vite |
| Database | PostgreSQL 17 |
| Cache | Redis 7 |
| Testing | pytest, Vitest, Playwright |
| CI/CD | GitHub Actions |
| Orchestration | Docker Compose |

## Bắt Đầu Nhanh

```bash
# Clone
git clone https://github.com/tqhoa/claude-ai-microservices.git
cd claude-ai-microservices

# Copy env
cp .env.example .env

# Khởi động tất cả services
docker compose up -d --build

# Chạy migration
docker compose exec backend alembic upgrade head

# Truy cập
# Frontend: http://localhost
# API docs: http://localhost/api/docs
# Health:   http://localhost/health
```

```bash
# Mở Claude Code và mô tả ứng dụng
claude

# Ví dụ prompt:
# "Tạo hệ thống quản lý người dùng với CRUD, auth JWT, và dashboard"
# "Thêm tính năng upload avatar với rate limiting"
# "Thiết lập E2E test cho luồng đăng nhập"
```

## Quy Tắc Quan Trọng

| Quy tắc | Giải thích |
|---------|-----------|
| Frontend → Gateway → Backend | Frontend KHÔNG BAO GIỜ gọi Backend trực tiếp |
| CORS chỉ ở Gateway | Backend không cần CORSMiddleware |
| API versioning `/api/v1/` | Tất cả endpoints có version prefix |
| Error format chuẩn | `{code, message, timestamp, path}` xuyên suốt |
| JWT auth via Gateway | Gateway forward Authorization header |
| Shared types | Frontend TS interfaces khớp Backend Pydantic schemas |
| Request ID tracing | X-Request-ID từ Gateway → Backend → logs |
| Health checks | Mỗi service có `/health` endpoint |

## Giới Thiệu

Mẫu Claude Code cho kiến trúc microservices hoàn chỉnh — API Gateway (Nginx) + Backend (FastAPI) + Frontend (Vue 3) với Docker Compose orchestration, tác nhân chuyên biệt, và kỹ năng chi tiết ở cả cấp hệ thống lẫn từng service. Phiên bản tiếng Việt.
