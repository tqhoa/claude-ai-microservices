# CLAUDE.md — Engine (FastAPI)

## Vai Trò
Engine API xử lý toàn bộ business logic, authentication, data access, và background tasks.

## Quy Tắc
- Python 3.12+ với async/await xuyên suốt
- FastAPI với `<script setup>` tương đương: mọi route handler đều async
- SQLAlchemy 2.0 async cho database access
- Pydantic v2 cho tất cả request/response schemas
- Alembic cho database migrations
- pytest + pytest-asyncio cho testing
- structlog cho structured JSON logging
- KHÔNG cấu hình CORS ở đây (Gateway xử lý)
- KHÔNG trả về SQLAlchemy models trực tiếp — luôn qua Pydantic response schema
- Mọi endpoint bắt đầu `/api/v1/`

## Cấu Trúc
```
engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory, lifespan, middleware
│   ├── config.py            # pydantic-settings
│   ├── database.py          # Engine, session, Base
│   ├── dependencies.py      # Shared dependencies (get_db, get_current_user)
│   ├── exceptions.py        # Custom exceptions + handlers
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   ├── api/
│   │   └── v1/              # API routers versioned
│   │       ├── router.py
│   │       ├── auth.py
│   │       └── users.py
│   └── utils/
│       └── security.py      # JWT, password hashing
├── alembic/
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── factories.py
├── tasks/
│   ├── lessons.md           # Bài học từ lỗi (Claude đọc đầu tiên)
│   └── decisions.md         # Quyết định kiến trúc (ADR)
├── CHANGELOG.md             # Lịch sử thay đổi
├── pyproject.toml
├── alembic.ini
└── Dockerfile
```

## Quy Trình Bắt Buộc (Bộ Nhớ Dài Hạn)

Claude PHẢI thực hiện các bước này:

### Bắt đầu phiên mới:
1. **ĐỌC** `tasks/lessons.md` — Tránh lặp lỗi cũ
2. **ĐỌC** `tasks/decisions.md` — Hiểu quyết định kiến trúc đã có
3. **ĐỌC** `CHANGELOG.md` — Biết trạng thái và lịch sử thay đổi

### Sau khi hoàn thành tính năng:
4. **CẬP NHẬT** `CHANGELOG.md` — Thêm entry vào [Chưa phát hành]

### Sau khi user sửa lỗi Claude:
5. **GHI** `tasks/lessons.md` — Thêm bài học mới (lỗi, nguyên nhân, sửa, quy tắc)

### Khi đưa ra quyết định kiến trúc:
6. **GHI** `tasks/decisions.md` — Thêm ADR mới (ngữ cảnh, quyết định, lý do, hệ quả)

### Files:
```
engine/
├── CHANGELOG.md          # Lịch sử thay đổi theo phiên bản
└── tasks/
    ├── lessons.md        # Bài học từ lỗi (bộ nhớ Claude)
    └── decisions.md      # Quyết định kiến trúc (ADR)
```

## Lệnh Phát Triển
```bash
# Trong Docker
docker compose exec engine pytest --cov=app
docker compose exec engine alembic upgrade head
docker compose exec engine alembic revision --autogenerate -m "description"

# Local
cd engine
uv sync
uv run pytest
uv run ruff check .
uv run mypy .
uv run uvicorn app.main:app --reload
```

## Error Response Chuẩn
Tất cả lỗi trả về format:
```json
{
  "code": "USER_NOT_FOUND",
  "message": "Không tìm thấy người dùng với ID 123",
  "timestamp": "2025-01-15T10:30:00Z",
  "path": "/api/v1/users/123"
}
```
