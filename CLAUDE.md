# CLAUDE.md — Dự Án Microservices

## Tổng Quan Kiến Trúc

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend   │────▶│   API Gateway    │────▶│    Backend      │
│  (Vue 3)    │     │ (Nginx/Traefik)  │     │   (FastAPI)     │
│  Port 3000  │     │   Port 80/443    │     │   Port 8000     │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                              ┌────────┼────────┐
                                              │        │        │
                                           ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
                                           │ DB  │ │Redis│ │Queue│
                                           │5432 │ │6379 │ │5672 │
                                           └─────┘ └─────┘ └─────┘
```

## Cấu Trúc Dự Án

```
.
├── api_gateway/          # Nginx reverse proxy + rate limiting + SSL
├── backend/              # FastAPI async API + SQLAlchemy + Alembic
├── frontend/             # Vue 3 + Nuxt + Pinia + TailwindCSS
├── docker-compose.yml    # Orchestration tất cả services
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .github/workflows/    # CI/CD pipeline
├── docs/                 # Tài liệu kiến trúc
└── CLAUDE.md            # File này
```

---

### 1. Mặc Định Chế Độ Lập Kế Hoạch
- Vào chế độ lập kế hoạch cho BẤT KỲ tác vụ nào ảnh hưởng nhiều hơn 1 service
- Khi thay đổi API contract → lập kế hoạch cập nhật cả backend lẫn frontend
- Viết đặc tả chi tiết trước, đặc biệt cho giao tiếp giữa các service

### 2. Vòng Lặp Tự Cải Thiện
- Sau BẤT KỲ lần sửa lỗi: cập nhật `tasks/lessons.md`
- Ghi lại bài học về tương tác giữa các service (CORS, auth flow, API versioning)

### 3. Xác Minh Trước Khi Hoàn Thành
- Chạy `docker-compose up` và xác minh end-to-end flow
- Test từ frontend → API gateway → backend → database
- Kiểm tra CORS, auth token flow, error propagation

### 4. Kỹ Năng & Tác Nhân
- Mỗi thư mục con (api_gateway, backend, frontend) có `.claude/` riêng
- Kỹ năng ở thư mục gốc `.claude/skills/` áp dụng cho cross-cutting concerns
- Tải kỹ năng cụ thể cho từng service khi cần

### 5. Tác Nhân Phụ
- Dùng tác nhân phụ cho tác vụ chỉ liên quan 1 service
- Tác vụ cross-service giữ trong ngữ cảnh chính

## Nguyên Tắc Cốt Lõi
- **API-First**: Thiết kế API contract trước khi code
- **Đơn Giản Trước**: Mỗi service càng đơn giản càng tốt
- **Không Lười Biếng**: Tìm nguyên nhân gốc rễ, không sửa tạm
- **Tách Biệt Rõ Ràng**: Mỗi service có trách nhiệm riêng

## Hướng Dẫn Chung

### API Gateway (api_gateway/)
- Nginx làm reverse proxy
- Rate limiting và request throttling
- SSL termination
- CORS headers
- Request/response logging
- Health check endpoints
- Load balancing (nếu nhiều backend instances)

### Backend (backend/)
- Python 3.12+ với FastAPI
- `<script setup lang="ts">` tương đương: async/await xuyên suốt
- SQLAlchemy 2.0 async + Alembic migrations
- Pydantic v2 cho tất cả schemas
- pytest + pytest-asyncio cho testing
- structlog cho structured logging

### Frontend (frontend/)
- Vue 3 Composition API + TypeScript strict
- Nuxt 3 cho SSR/SSG (tùy chọn)
- Pinia cho quản lý trạng thái
- TailwindCSS cho styling
- Vitest + Vue Test Utils cho testing
- Axios/ofetch cho HTTP client

### Quy Tắc Chung
- Docker Compose cho development và production
- GitHub Actions cho CI/CD
- Semantic versioning cho mỗi service
- Biến môi trường qua `.env` files
- Không hard-code URLs giữa services
- API versioning (`/api/v1/`)
- Shared types/contracts giữa frontend và backend
- Structured logging JSON cho tất cả services
