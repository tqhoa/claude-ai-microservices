# Nhật Ký Thay Đổi (Changelog)

Tất cả thay đổi đáng chú ý của Engine service được ghi lại ở đây.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Chưa phát hành]

### Thêm mới
- Khởi tạo dự án FastAPI với cấu trúc microservices
- Cấu hình SQLAlchemy 2.0 async + Alembic migrations
- Hệ thống xác thực JWT (đăng ký, đăng nhập, refresh token)
- CRUD endpoints cho User entity
- Health check endpoints (/health, /ready)
- Structured logging với structlog (JSON format)
- Docker multi-stage build (development + production targets)
- pytest + pytest-asyncio test infrastructure
- Hệ thống phân quyền ACL: User → Role → Permission (many-to-many)
- API routes: /api/v1/auth, /api/v1/users, /api/v1/roles, /api/v1/permissions
- Dependency `require_permission(codename)` cho route-level ACL
- Permission codename format: `resource.action` (vd: users.read, roles.manage)

### Thay đổi
- (chưa có)

### Sửa lỗi
- (chưa có)

### Xóa bỏ
- (chưa có)

---

<!-- MẪU CHO BẢN PHÁT HÀNH MỚI:

## [X.Y.Z] - YYYY-MM-DD

### Thêm mới
- Tính năng mới

### Thay đổi
- Thay đổi hành vi hiện có

### Sửa lỗi
- Sửa lỗi

### Xóa bỏ
- Tính năng/API bị loại bỏ

### Bảo mật
- Sửa lỗ hổng bảo mật

### Hiệu suất
- Cải thiện hiệu suất

### Nợ kỹ thuật
- Tái cấu trúc, cleanup, cải thiện nội bộ

-->
