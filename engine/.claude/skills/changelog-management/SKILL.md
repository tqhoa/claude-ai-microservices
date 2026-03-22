---
name: quan-ly-changelog
description: Quản lý CHANGELOG.md, lessons learned, và architecture decisions cho Backend. Sử dụng LUÔN khi bắt đầu phiên mới, sau khi sửa lỗi, hoặc khi thêm tính năng. Claude PHẢI đọc file này trước khi code.
---

# Kỹ Năng Quản Lý Changelog & Bài Học

Hệ thống theo dõi thay đổi, bài học, và quyết định kiến trúc giúp Claude Code liên tục cải thiện chất lượng output.

---

## Tại Sao Quan Trọng?

Claude Code không có bộ nhớ giữa các phiên. Hệ thống 3 file sau đây là **bộ nhớ dài hạn** của dự án:

| File | Mục đích | Khi nào đọc | Khi nào viết |
|------|----------|-------------|--------------|
| `CHANGELOG.md` | Lịch sử thay đổi theo phiên bản | Bắt đầu phiên mới | Sau mỗi tính năng/sửa lỗi |
| `tasks/lessons.md` | Bài học từ lỗi đã mắc | **ĐẦU TIÊN** khi bắt đầu phiên | Sau mỗi lần user sửa lỗi Claude |
| `tasks/decisions.md` | Quyết định kiến trúc & lý do | Trước khi thay đổi kiến trúc | Khi đưa ra quyết định mới |

---

## Quy Trình Bắt Buộc

### 1. Bắt Đầu Phiên Mới → ĐỌC

```
Claude bắt đầu phiên:
  1. Đọc tasks/lessons.md        ← Tránh lặp lỗi cũ
  2. Đọc tasks/decisions.md      ← Hiểu quyết định đã có
  3. Đọc CHANGELOG.md            ← Biết trạng thái hiện tại
  4. Bắt đầu code
```

### 2. Sau Khi User Sửa Lỗi Claude → GHI BÀI HỌC

```
User chỉ ra lỗi Claude mắc:
  1. Sửa lỗi
  2. Thêm entry mới vào tasks/lessons.md:
     ### [YYYY-MM-DD] Mô tả ngắn
     - **Lỗi**: Cụ thể Claude đã làm gì sai
     - **Nguyên nhân**: Tại sao
     - **Sửa**: Cách sửa đúng
     - **Quy tắc**: Quy tắc mới để tránh lặp
     - **File liên quan**: Files bị ảnh hưởng
```

### 3. Sau Khi Hoàn Thành Tính Năng → CẬP NHẬT CHANGELOG

```
Hoàn thành tính năng hoặc sửa lỗi:
  1. Thêm entry vào CHANGELOG.md mục [Chưa phát hành]
  2. Phân loại đúng: Thêm mới / Thay đổi / Sửa lỗi / Xóa bỏ
  3. Mô tả ngắn gọn, rõ ràng
```

### 4. Quyết Định Kiến Trúc → GHI ADR

```
Khi đưa ra quyết định kiến trúc quan trọng:
  1. Thêm ADR mới vào tasks/decisions.md
  2. Ghi rõ: Ngữ cảnh → Quyết định → Lý do → Hệ quả
  3. Không bao giờ xóa ADR cũ (đánh dấu "Thay thế" nếu thay đổi)
```

---

## Mẫu Changelog Entry

```markdown
## [Chưa phát hành]

### Thêm mới
- Thêm endpoint POST /api/v1/users/avatar cho upload avatar
- Thêm rate limiting cho upload endpoints (10 req/phút)
- Thêm resize ảnh tự động khi upload (max 500x500px)

### Thay đổi
- Đổi response format UserResponse thêm trường avatar_url

### Sửa lỗi
- Sửa lỗi N+1 query trong GET /api/v1/users (thêm selectinload)
- Sửa lỗi 500 khi email trùng lặp (trả về 409 Conflict)

### Hiệu suất
- Tối ưu query danh sách users: thêm index trên email column
```

---

## Mẫu Lesson Entry

```markdown
### [2025-01-15] N+1 query trong danh sách users
- **Lỗi**: GET /api/v1/users trả về chậm khi có nhiều users
- **Nguyên nhân**: Lazy loading user.orders → N+1 queries
- **Sửa**: Thêm `.options(selectinload(User.orders))` vào query
- **Quy tắc**: LUÔN dùng selectinload cho relationships trong list endpoints. Grep `lazy` trong models để kiểm tra
- **File liên quan**: `app/repositories/user.py`, `app/models/user.py`
```

---

## Mẫu ADR Entry

```markdown
### ADR-006: Redis cho session storage thay vì JWT stateless
- **Ngày**: 2025-01-15
- **Trạng thái**: Chấp nhận
- **Ngữ cảnh**: Cần khả năng revoke token ngay lập tức (ví dụ: user bị ban)
- **Quyết định**: Lưu session trong Redis, JWT chỉ làm session ID
- **Lý do**: JWT stateless không thể revoke trước khi hết hạn
- **Hệ quả**: Thêm Redis dependency, mỗi request cần lookup Redis, nhưng có thể force logout
```

---

## Tích Hợp Với CLAUDE.md

Thêm vào CLAUDE.md backend:

```markdown
### Quy Trình Bắt Buộc
1. ĐỌC `tasks/lessons.md` trước khi bắt đầu code
2. ĐỌC `tasks/decisions.md` trước khi thay đổi kiến trúc
3. CẬP NHẬT `CHANGELOG.md` sau mỗi tính năng/sửa lỗi
4. GHI `tasks/lessons.md` sau mỗi lần user sửa lỗi
```

---

## Kiểm Tra Tự Động

```bash
# Kiểm tra CHANGELOG.md có entry cho version hiện tại
grep -c "Chưa phát hành" CHANGELOG.md

# Kiểm tra lessons.md có nội dung
wc -l tasks/lessons.md

# Kiểm tra decisions.md có ADR entries  
grep -c "^### ADR-" tasks/decisions.md

# Lệnh cho Claude: đọc context trước khi code
cat tasks/lessons.md tasks/decisions.md CHANGELOG.md
```

---

## Bảng Kiểm Tra

- [ ] `CHANGELOG.md` tồn tại và có format đúng
- [ ] `tasks/lessons.md` tồn tại và được cập nhật sau lỗi
- [ ] `tasks/decisions.md` tồn tại với các ADR quan trọng
- [ ] CLAUDE.md tham chiếu đến 3 file này
- [ ] Claude đọc lessons.md đầu tiên khi bắt đầu phiên
- [ ] Claude cập nhật changelog sau mỗi tính năng
- [ ] Claude ghi bài học sau mỗi lần bị sửa lỗi
- [ ] Không ADR nào bị xóa (chỉ đánh dấu thay thế)
