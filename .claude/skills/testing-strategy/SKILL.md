---
name: chien-luoc-kiem-thu
description: Chiến lược kiểm thử cho microservices bao gồm test pyramid, contract testing, E2E, và test trong Docker. Sử dụng khi lập kế hoạch kiểm thử hoặc thiết lập test infrastructure.
---

# Kỹ Năng Chiến Lược Kiểm Thử

Chiến lược test đa tầng cho hệ thống microservices.

## Kim Tự Tháp Test

```
              /      E2E (Playwright)       \    ← 5-10 luồng chính
             /   Gateway Tests (curl/httpx)  \   ← Routing, CORS, headers
            /    Integration (per service)    \  ← Service + DB + Redis
           /     Component (Vue Test Utils)    \ ← UI components
          /      Unit (Vitest/pytest)            \← Logic thuần
```

## Test Mỗi Service

### Backend (pytest)
```bash
cd backend
pytest tests/unit/           # Logic thuần, nhanh
pytest tests/integration/    # Cần DB (Docker service)
pytest tests/api/            # Endpoint tests
pytest --cov=app            # Tất cả + coverage
```

### Frontend (Vitest)
```bash
cd frontend
pnpm test                   # Unit + component tests
pnpm test:e2e               # Playwright E2E
```

### Gateway (shell + curl)
```bash
# Test trong Docker
docker compose up -d
./tests/gateway/test_routing.sh
./tests/gateway/test_cors.sh
./tests/gateway/test_rate_limit.sh
```

## Contract Testing

```typescript
// Đảm bảo Frontend types khớp Backend schemas
// frontend/src/types/user.ts
interface User {
  id: number
  email: string
  firstName: string
  lastName: string
  createdAt: string
}

// So sánh với backend/app/schemas/user.py
// class UserResponse(BaseModel):
//     id: int
//     email: str
//     first_name: str  ← MISMATCH! camelCase vs snake_case
//     last_name: str
//     created_at: datetime
```

Giải pháp: Backend dùng `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` để tự động chuyển đổi.

## Bảng Kiểm Tra
- [ ] Backend: unit + integration + API tests (> 80% coverage)
- [ ] Frontend: component + composable tests (> 80% coverage)
- [ ] Gateway: routing + CORS + rate limit tests
- [ ] E2E: 5-10 luồng quan trọng nhất
- [ ] Contract: Frontend types khớp Backend schemas
- [ ] CI: tất cả tests chạy tự động
- [ ] Docker test environment reproducible
