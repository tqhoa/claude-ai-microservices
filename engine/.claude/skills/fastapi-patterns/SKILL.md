---
name: fastapi-patterns
description: Mẫu FastAPI cho Backend microservice. Project structure, DI, error handling.
---
# Mẫu FastAPI

## Cấu Trúc Router
```python
# app/api/v1/router.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1")
router.include_router(auth_router, prefix="/auth", tags=["Xác thực"])
router.include_router(users_router, prefix="/users", tags=["Người dùng"])
```

## Chuỗi Dependency Injection
```
get_db() → get_repository() → get_service() → get_current_user()
```

## Phản Hồi Lỗi Chuẩn
```python
class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, resource: str, id: int | str):
        super().__init__(
            f"{resource.upper()}_NOT_FOUND",
            f"Không tìm thấy {resource} với ID {id}",
            404,
        )
```
