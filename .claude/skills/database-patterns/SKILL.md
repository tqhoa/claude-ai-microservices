---
name: mau-co-so-du-lieu
description: Mẫu quản lý cơ sở dữ liệu cho microservices bao gồm migration, connection pooling, backup, và Redis caching. Sử dụng khi thiết lập hoặc tối ưu database.
---

# Kỹ Năng Mẫu Cơ Sở Dữ Liệu

Quản lý PostgreSQL + Redis cho hệ thống microservices.

## Migration Strategy

```bash
# Chạy migration khi khởi động service (trong CI/CD hoặc init container)
docker compose exec engine alembic upgrade head

# Tạo migration mới
docker compose exec engine alembic revision --autogenerate -m "add_users_table"

# Rollback
docker compose exec engine alembic downgrade -1
```

## Connection Pool Tuning

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Kết nối cơ sở
    max_overflow=10,       # Kết nối thêm khi tải cao
    pool_recycle=3600,     # Tái sử dụng sau 1 giờ
    pool_pre_ping=True,    # Kiểm tra kết nối trước khi dùng
)
# Quy tắc: pool_size = số concurrent requests / số app instances
```

## Redis Caching Pattern

```python
class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_or_set(self, key: str, factory, ttl: int = 300):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        value = await factory()
        await self.redis.set(key, json.dumps(value), ex=ttl)
        return value

    async def invalidate(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## Docker Compose Database

```yaml
db:
  image: postgres:17-alpine
  environment:
    POSTGRES_DB: ${DB_NAME}
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - pgdata:/var/lib/postgresql/data
    - ./engine/scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    retries: 5
```
