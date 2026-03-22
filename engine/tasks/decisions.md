# Nhật Ký Quyết Định (Architecture Decision Records)

Ghi lại các quyết định kiến trúc quan trọng và lý do đằng sau.
Claude PHẢI tham khảo file này trước khi đề xuất thay đổi kiến trúc.

---

## Format

```
### ADR-XXX: Tiêu đề
- **Ngày**: YYYY-MM-DD
- **Trạng thái**: Đề xuất | Chấp nhận | Thay thế bởi ADR-YYY
- **Ngữ cảnh**: Vấn đề cần giải quyết
- **Quyết định**: Giải pháp được chọn
- **Lý do**: Tại sao chọn giải pháp này
- **Hệ quả**: Tác động của quyết định
```

---

## Quyết Định

### ADR-001: SQLAlchemy 2.0 Async thay vì Sync
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Cần chọn ORM và kiểu truy cập database
- **Quyết định**: SQLAlchemy 2.0 với asyncpg driver
- **Lý do**: FastAPI là async framework, dùng sync ORM sẽ block event loop. SQLAlchemy 2.0 hỗ trợ async native với API hiện đại
- **Hệ quả**: Cần `async with` cho sessions, `expire_on_commit=False`, và `selectinload` thay vì lazy loading

### ADR-002: Repository Pattern cho Data Access
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Cần tách biệt logic truy cập dữ liệu khỏi business logic
- **Quyết định**: Dùng Repository classes inject qua FastAPI Depends()
- **Lý do**: Dễ test (mock repository), dễ thay đổi data source, Single Responsibility
- **Hệ quả**: Thêm 1 layer abstraction, nhưng code dễ test và bảo trì hơn

### ADR-003: CORS chỉ ở API Gateway
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: CORS cần cấu hình cho frontend gọi API
- **Quyết định**: CORS headers chỉ ở Nginx Gateway, Backend không có CORSMiddleware
- **Lý do**: Tránh xung đột headers, single source of truth, Gateway là nơi phù hợp nhất
- **Hệ quả**: Backend development local cần chạy qua Gateway (docker-compose) hoặc dùng proxy

### ADR-004: Pydantic v2 alias_generator cho camelCase API
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Frontend dùng camelCase, Python dùng snake_case
- **Quyết định**: Pydantic schemas dùng `alias_generator=to_camel` + `populate_by_name=True`
- **Lý do**: API trả về camelCase (chuẩn JSON), Python code vẫn dùng snake_case
- **Hệ quả**: Frontend TypeScript interfaces khớp trực tiếp với API response

### ADR-006: ACL Feature-Based Permissions (User → Role → Permission)
- **Ngày**: 2026-03-22
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Cần hệ thống phân quyền linh hoạt cho features/resources
- **Quyết định**: Many-to-many: User ↔ Role ↔ Permission. Permission codename format `resource.action`. Dependency factory `require_permission(codename)` check ở route level. Superuser bypass tất cả. Roles và permissions loaded eagerly (`lazy="selectin"`) để check in-memory
- **Lý do**: Linh hoạt hơn role-based thuần (có thể gán permission trực tiếp cho role), dễ mở rộng khi thêm resources mới, codename format scannable và greppable
- **Hệ quả**: Cần seed default roles/permissions khi deploy. Permission check O(roles × permissions) nhưng thường rất nhỏ. Frontend cần biết user permissions để ẩn/hiện UI

### ADR-005: Structured Logging với structlog
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Cần logging nhất quán để debug trong microservices
- **Quyết định**: structlog với JSON output, propagate X-Request-ID từ Gateway
- **Lý do**: JSON logs dễ parse bằng ELK/Grafana, request_id giúp trace xuyên services
- **Hệ quả**: Mọi log phải dùng structlog key-value, không dùng print() hoặc f-string logging
