# Nhật Ký Thay Đổi (Changelog)

Tất cả thay đổi đáng chú ý của hệ thống Microservices được ghi lại ở đây.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Chưa phát hành]

### Thêm mới
- Docker Compose orchestration cho toàn bộ hệ thống microservices
  - `docker-compose.yml` — base config (gateway, engine, frontend, db, redis)
  - `docker-compose.dev.yml` — development override (hot reload, debug ports)
  - `docker-compose.prod.yml` — production override (replicas, resource limits)
- Network isolation: `frontend-net` và `backend-net` tách biệt
- Health checks cho gateway, engine, db, redis
- `.env.example` template cho team
- `Makefile` với lệnh tắt cho development workflow

### Thay đổi
- Đổi tên `backend/` → `engine/` — service engine quản lý users và phân quyền ACL

### Sửa lỗi
- (chưa có)
