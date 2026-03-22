---
name: microservices-patterns
description: Mẫu giao tiếp microservices, API contract design, error propagation, và data consistency. Sử dụng khi thiết kế giao tiếp giữa services hoặc giải quyết vấn đề cross-service.
---

# Kỹ Năng Mẫu Microservices

Mẫu giao tiếp và thiết kế cho hệ thống API Gateway + Engine + Frontend.

---

## API Contract Chuẩn Hóa

```typescript
// shared/types/api.ts — Types dùng chung giữa Frontend và Engine

// Response wrapper chuẩn
interface ApiResponse<T> {
  data: T
  meta?: {
    total: number
    page: number
    size: number
    pages: number
  }
}

// Error response chuẩn
interface ApiError {
  code: string        // "USER_NOT_FOUND", "VALIDATION_ERROR"
  message: string     // "Không tìm thấy người dùng với ID 123"
  timestamp: string   // ISO 8601
  path: string        // "/api/v1/users/123"
  details?: Array<{   // Chi tiết lỗi validation
    field: string
    message: string
  }>
}
```

```python
# engine/app/schemas/common.py — Tương ứng ở Engine
from pydantic import BaseModel
from datetime import datetime

class ErrorResponse(BaseModel):
    code: str
    message: str
    timestamp: datetime
    path: str
    details: list[dict] | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta

class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int
```

---

## Error Propagation

```
Engine Exception
    │
    ▼
FastAPI exception_handler → HTTP Response (chuẩn ErrorResponse)
    │
    ▼
Nginx Gateway → Forward nguyên vẹn (không modify body)
    │
    ▼
Frontend axios interceptor → Phân loại và hiển thị
    ├── 400 Validation → Hiển thị lỗi field cụ thể
    ├── 401 Unauthorized → Redirect /login
    ├── 403 Forbidden → Hiển thị "Không có quyền"
    ├── 404 Not Found → Hiển thị "Không tìm thấy"
    ├── 429 Rate Limited → Hiển thị "Quá nhiều yêu cầu"
    └── 500 Server Error → Hiển thị "Lỗi hệ thống"
```

```typescript
// frontend/src/api/client.ts
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const status = error.response?.status
    const apiError = error.response?.data

    switch (status) {
      case 401:
        authStore.logout()
        router.push({ name: 'login' })
        break
      case 403:
        toast.error('Bạn không có quyền thực hiện thao tác này')
        break
      case 422:
        // Trả về để form handler xử lý field errors
        break
      case 429:
        toast.warning('Quá nhiều yêu cầu, vui lòng thử lại sau')
        break
      default:
        toast.error(apiError?.message ?? 'Đã xảy ra lỗi')
    }
    return Promise.reject(error)
  }
)
```

---

## Service Communication Rules

| Quy tắc | Giải thích |
|---------|-----------|
| Frontend → Gateway → Engine | Frontend KHÔNG BAO GIỜ gọi Engine trực tiếp |
| Gateway chỉ routing + security | Không business logic ở Gateway |
| Engine là nguồn sự thật | Auth, validation, business logic đều ở Engine |
| Shared types | Frontend TypeScript types phải khớp Engine Pydantic schemas |
| API versioning | Tất cả endpoints bắt đầu `/api/v1/` |
| Health checks | Mỗi service có `/health` endpoint |

---

## Environment Variables Flow

```bash
# .env (gốc — Docker Compose đọc)
DB_PASSWORD=secure_password_here
SECRET_KEY=jwt_secret_key_here
REDIS_URL=redis://redis:6379/0

# Engine đọc qua Docker Compose environment:
# DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/appdb

# Frontend đọc qua build args:
# VITE_API_URL=/api  (relative, Gateway sẽ proxy)

# Gateway đọc qua nginx.conf (hardcoded service names trong Docker network)
# proxy_pass http://engine:8000;
```

---

## Bảng Kiểm Tra
- [ ] API response format nhất quán (ApiResponse<T> wrapper)
- [ ] Error format nhất quán (ErrorResponse)
- [ ] Frontend types khớp Engine schemas
- [ ] Tất cả endpoints versioned (/api/v1/)
- [ ] Frontend không gọi Engine trực tiếp
- [ ] Health checks cho mọi service
- [ ] Environment variables qua .env file
- [ ] Docker Compose dependencies đúng (depends_on + healthcheck)
