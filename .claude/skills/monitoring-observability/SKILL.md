---
name: giam-sat-quan-sat
description: Monitoring và observability xuyên microservices bao gồm structured logging, metrics, health checks, và request tracing. Sử dụng khi thiết lập giám sát hoặc debug vấn đề cross-service.
---

# Kỹ Năng Giám Sát & Quan Sát

Structured logging và monitoring nhất quán xuyên tất cả services.

## Request ID Tracing

```
Client → Gateway (tạo X-Request-ID: uuid)
    → Backend (log với request_id)
    → Response (header X-Request-ID)
    → Frontend (log errors với request_id)
```

```nginx
# Gateway: tạo request ID
add_header X-Request-ID $request_id always;
proxy_set_header X-Request-ID $request_id;
```

```python
# Backend: middleware log request ID
@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

```typescript
// Frontend: gắn request ID vào error report
apiClient.interceptors.response.use(null, (error) => {
  const requestId = error.response?.headers?.['x-request-id']
  console.error(`[${requestId}] API Error:`, error.message)
  // Gửi tới Sentry với request_id tag
})
```

## Health Checks Chuẩn Hóa

```python
# Backend /health
@router.get("/health")
async def health():
    return {"status": "healthy", "service": "backend", "version": "1.0.0"}

# Backend /ready (kiểm tra dependencies)
@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected", "redis": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})
```

## Log Format Nhất Quán

Tất cả services output JSON logs:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "service": "backend",
  "request_id": "abc-123",
  "event": "request_completed",
  "method": "POST",
  "path": "/api/v1/users",
  "status": 201,
  "duration_ms": 45
}
```
