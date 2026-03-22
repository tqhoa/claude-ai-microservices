# Bài Học Rút Ra (Lessons Learned)

File này được Claude tự động cập nhật sau mỗi lần sửa lỗi từ người dùng.
Claude PHẢI xem lại file này khi bắt đầu phiên làm việc mới.

---

## Quy Tắc Ghi Bài Học

Mỗi bài học theo format:

```
### [YYYY-MM-DD] Tiêu đề ngắn
- **Lỗi**: Mô tả lỗi đã mắc
- **Nguyên nhân**: Tại sao lỗi xảy ra
- **Sửa**: Cách sửa đúng
- **Quy tắc**: Quy tắc để không lặp lại
- **File liên quan**: Danh sách files bị ảnh hưởng
```

---

## Bài Học

<!-- Claude sẽ thêm bài học mới ở đây -->

### [Mẫu] Không cấu hình CORS ở Backend
- **Lỗi**: Thêm CORSMiddleware vào FastAPI app
- **Nguyên nhân**: Quên rằng CORS được xử lý ở API Gateway (Nginx)
- **Sửa**: Xóa CORSMiddleware, để Gateway xử lý CORS headers
- **Quy tắc**: CORS chỉ cấu hình tại `api_gateway/nginx.conf` — Backend KHÔNG BAO GIỜ có CORSMiddleware
- **File liên quan**: `app/main.py`, `api_gateway/nginx.conf`

### [Mẫu] Trả về SQLAlchemy model trực tiếp
- **Lỗi**: `return await db.get(User, user_id)` trong route handler
- **Nguyên nhân**: Lười tạo Pydantic response schema
- **Sửa**: Tạo `UserResponse(BaseModel)` với `model_config = ConfigDict(from_attributes=True)`
- **Quy tắc**: LUÔN dùng `response_model=UserResponse` trên endpoint, KHÔNG BAO GIỜ trả ORM model trực tiếp
- **File liên quan**: `app/api/v1/users.py`, `app/schemas/user.py`

### [Mẫu] Sync call trong async handler
- **Lỗi**: Dùng `requests.get()` hoặc `time.sleep()` trong async function
- **Nguyên nhân**: Không nhận ra đang block event loop
- **Sửa**: Dùng `httpx.AsyncClient` và `asyncio.sleep()`
- **Quy tắc**: Trong async function — chỉ dùng async libraries. Grep `import requests` để phát hiện
- **File liên quan**: Bất kỳ file nào trong `app/`
