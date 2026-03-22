# Quy Tắc Code — Toàn Hệ Thống

> Claude PHẢI đọc file này trước khi viết bất kỳ dòng code nào.
> Vi phạm bất kỳ quy tắc nào dưới đây = lỗi cần sửa ngay.

---

## 1. Quy Tắc Kiến Trúc (Không Bao Giờ Vi Phạm)

### 1.1 Luồng giao tiếp
```
Frontend → Gateway → Backend → Database/Redis
         ↑ KHÔNG BAO GIỜ bỏ qua Gateway
```

- Frontend gọi API qua đường dẫn tương đối `/api/v1/` — Gateway proxy sang Backend
- Frontend KHÔNG BAO GIỜ chứa URL `http://localhost:8000` hoặc bất kỳ direct backend URL nào
- Backend KHÔNG expose port ra ngoài Docker network (chỉ Gateway truy cập được)

### 1.2 CORS
- CORS **CHỈ** cấu hình tại `api_gateway/nginx.conf`
- Backend **KHÔNG CÓ** `CORSMiddleware` — nếu thấy, XÓA ngay
- Frontend không cần xử lý CORS — Gateway đã thêm headers

### 1.3 API versioning
- Tất cả endpoints backend bắt đầu `/api/v1/`
- Router prefix: `APIRouter(prefix="/api/v1")`
- Khi có breaking change → tạo `/api/v2/`, giữ v1 hoạt động

### 1.4 Error format
Tất cả lỗi từ Backend trả về cùng 1 format, không ngoại lệ:
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Mô tả lỗi bằng ngôn ngữ người dùng hiểu",
  "timestamp": "2025-01-15T10:30:00Z",
  "path": "/api/v1/users/123",
  "details": []
}
```
- Gateway forward nguyên vẹn — không modify response body
- Frontend xử lý dựa trên HTTP status code + `code` field

### 1.5 Authentication flow
```
Frontend gửi → Authorization: Bearer <JWT> header
Gateway forward header nguyên vẹn → Backend validate JWT
401 → Frontend redirect /login
403 → Frontend hiển thị "Không có quyền"
```
- Token: httpOnly cookie hoặc in-memory (KHÔNG localStorage)
- Access token: 15 phút, Refresh token: 7 ngày
- Backend là nơi DUY NHẤT validate JWT

---

## 2. Quy Tắc Đặt Tên

### 2.1 Xuyên suốt
| Đối tượng | Quy tắc | Ví dụ |
|-----------|---------|-------|
| File/folder | snake_case | `user_service.py`, `auth-store.ts` |
| Branch Git | kebab-case | `feature/add-user-avatar` |
| Commit | Conventional Commits | `feat(backend): add user avatar upload` |
| API endpoint | kebab-case, số nhiều | `GET /api/v1/users`, `POST /api/v1/order-items` |
| Biến môi trường | UPPER_SNAKE_CASE | `DATABASE_URL`, `SECRET_KEY` |

### 2.2 Backend (Python)
| Đối tượng | Quy tắc | Ví dụ |
|-----------|---------|-------|
| Class | PascalCase | `UserService`, `OrderRepository` |
| Function/method | snake_case | `get_user_by_id`, `create_order` |
| Variable | snake_case | `user_count`, `is_active` |
| Constant | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE = 100` |
| Pydantic schema | PascalCase + hậu tố | `UserCreate`, `UserResponse`, `UserUpdate` |
| SQLAlchemy model | PascalCase số ít | `User`, `OrderItem` |
| Database table | snake_case số nhiều | `users`, `order_items` |
| Pydantic → JSON | camelCase (alias_generator) | `firstName`, `createdAt` |

### 2.3 Frontend (TypeScript/Vue)
| Đối tượng | Quy tắc | Ví dụ |
|-----------|---------|-------|
| Component | PascalCase | `UserCard.vue`, `BaseButton.vue` |
| Composable | camelCase + tiền tố use | `useAuth.ts`, `usePagination.ts` |
| Pinia store | camelCase + tiền tố use | `useAuthStore`, `useCartStore` |
| Interface/Type | PascalCase | `User`, `ApiResponse<T>` |
| Variable/function | camelCase | `userName`, `fetchUsers()` |
| CSS class | kebab-case | `user-card`, `btn-primary` |
| Event emit | kebab-case | `@update:model-value`, `@item-selected` |
| Props | camelCase | `:userName`, `:isActive` |

---

## 3. Quy Tắc Code Backend (Python/FastAPI)

### 3.1 Bắt buộc
```python
# ✅ BẮT BUỘC
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Luôn có type hints, luôn async, luôn Depends()."""

# ❌ CẤM
def get_user(user_id, db):  # Thiếu types, sync, không Depends
    """Cấm viết như này."""
```

- **Luôn async/await** — không function sync nào trong `app/`
- **Luôn type hints** — mọi function, mọi parameter, mọi return type
- **Luôn Pydantic schema** cho request/response — không `dict`, không ORM model trực tiếp
- **Luôn `response_model`** trên mọi endpoint
- **Luôn `Depends()`** cho dependency injection — không import trực tiếp
- **Không `print()`** — chỉ `structlog.get_logger()`
- **Không `any` type** — nếu không biết type, dùng `object` hoặc generic `T`
- **Không raw SQL** — chỉ SQLAlchemy ORM hoặc `text()` với parameterized queries

### 3.2 Cấu trúc tầng
```
Request → Router (validation) → Service (logic) → Repository (DB) → Response
          Pydantic schema         Business rules     SQLAlchemy        Pydantic schema
```
- Router: KHÔNG chứa business logic, chỉ validate input + gọi service + trả response
- Service: business logic thuần, nhận/trả Pydantic schemas hoặc domain objects
- Repository: CRUD + queries, nhận/trả SQLAlchemy models
- KHÔNG gọi Repository trực tiếp từ Router — luôn qua Service

### 3.3 Database
- `expire_on_commit=False` trong async session — bắt buộc
- `selectinload()` cho mọi relationship trong list queries — ngăn N+1
- `lazy="raise"` trên model relationships — phát hiện N+1 sớm
- Index cho mọi FK column và column hay filter/sort
- Migration mới = `alembic revision --autogenerate -m "mô_tả"`

### 3.4 Error handling
```python
# ✅ Đúng: exception cụ thể
try:
    user = await service.get_user(user_id)
except UserNotFoundError:
    raise  # Để global handler xử lý

# ❌ Sai: catch Exception chung
try:
    user = await service.get_user(user_id)
except Exception:
    raise HTTPException(status_code=500)  # Nuốt lỗi
```
- Dùng exception hierarchy từ `app/exceptions.py`
- KHÔNG catch `Exception` chung trừ khi log + re-raise
- KHÔNG `raise HTTPException` trong service layer — chỉ raise `AppException`
- Global exception handler chuyển `AppException` → HTTP response

---

## 4. Quy Tắc Code Frontend (Vue.js/TypeScript)

### 4.1 Bắt buộc
```vue
<!-- ✅ BẮT BUỘC: script setup + lang="ts" -->
<script setup lang="ts">
interface Props {
  user: User
}
const props = defineProps<Props>()
const emit = defineEmits<{ edit: [user: User] }>()
</script>

<!-- ❌ CẤM: Options API -->
<script>
export default {
  props: { user: Object },
  methods: { ... }
}
</script>
```

- **Luôn `<script setup lang="ts">`** — không Options API, không `<script>` thuần
- **Luôn typed props** — `defineProps<Props>()` với interface
- **Luôn typed emits** — `defineEmits<{ event: [payload] }>()`
- **Không `any`** — không `@ts-ignore` — dùng `@ts-expect-error` nếu bắt buộc kèm comment lý do
- **Không `v-html`** với dữ liệu người dùng — XSS risk
- **Không `console.log`** trong production code — dùng logger hoặc xóa
- **Không `localStorage`** cho JWT tokens — dùng httpOnly cookie hoặc memory

### 4.2 Component rules
- Mỗi component < 200 dòng — nếu dài hơn, tách
- Mỗi component 1 trách nhiệm — không "god component"
- Base components: tiền tố `Base` (`BaseButton`, `BaseInput`, `BaseModal`)
- Layout components: tiền tố `App` (`AppHeader`, `AppSidebar`)
- Mọi API call phải có 3 states: loading, error, empty/data

### 4.3 State management
```typescript
// ✅ Đúng: Pinia setup syntax
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!user.value)
  async function login(credentials: LoginForm) { ... }
  return { user, isAuthenticated, login }
})

// ❌ Sai: Options syntax
export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null }),
})
```
- Pinia: setup syntax (`() => { }`) — không options syntax
- Composables cho logic tái sử dụng — không mixins
- Props/emits cho parent-child 1-2 cấp — không over-use store

### 4.4 API integration
```typescript
// ✅ Đúng: relative URL qua gateway
const api = axios.create({ baseURL: '/api/v1' })

// ❌ Sai: direct backend URL
const api = axios.create({ baseURL: 'http://localhost:8000' })
```
- Axios/ofetch instance centralized trong `src/api/client.ts`
- Request interceptor gắn JWT token
- Response interceptor: 401 → redirect login, 500 → toast error
- TypeScript interfaces cho API responses — PHẢI khớp backend Pydantic schemas

---

## 5. Quy Tắc API Gateway (Nginx)

- CORS headers CHỈ ở đây — nguồn sự thật duy nhất
- Rate limiting: auth endpoints 5/phút, API chung 30/giây
- Security headers đầy đủ (X-Frame-Options, CSP, HSTS, v.v.)
- X-Request-ID: tạo mới nếu không có, forward cho backend
- Access log format JSON
- SPA fallback: `try_files $uri $uri/ /index.html`
- WebSocket proxy cho `/ws/` (nếu cần)
- `nginx -t` PHẢI pass trước khi commit

---

## 6. Quy Tắc Git & CI/CD

### 6.1 Commit messages
```
<loại>(<phạm vi>): <mô tả ngắn>

Ví dụ:
feat(backend): thêm endpoint upload avatar
fix(frontend): sửa lỗi redirect sau đăng nhập
refactor(gateway): tách CORS config thành file riêng
docs: cập nhật README hướng dẫn Docker
```

Loại: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `security`
Phạm vi: `backend`, `frontend`, `gateway`, `docker`, `ci`

### 6.2 Branch strategy
- `main` — production-ready, merge qua PR
- `develop` — integration branch
- `feature/<tên>` — tính năng mới
- `fix/<tên>` — sửa lỗi
- `hotfix/<tên>` — sửa lỗi khẩn cấp từ main

### 6.3 Trước khi commit
```bash
# Backend
cd backend && ruff check . && mypy . && pytest --cov=app

# Frontend  
cd frontend && pnpm lint && pnpm type-check && pnpm test

# Gateway
docker run --rm -v $(pwd)/api_gateway/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t

# Docker
docker compose config --quiet
```

---

## 7. Quy Tắc Testing

### 7.1 Bắt buộc
- Mỗi endpoint mới = ít nhất 2 tests (1 positive + 1 negative)
- Mỗi service method mới = unit test
- Coverage > 80% — CI block merge nếu dưới
- Không test implementation — chỉ test behavior
- Test data dùng factory — không hard-code

### 7.2 Naming
```python
# Backend: test_<hành_vi>_<kết_quả_mong_đợi>
def test_create_user_returns_201()
def test_create_user_duplicate_email_returns_409()
def test_get_user_not_found_returns_404()
def test_delete_product_unauthorized_returns_401()
```

```typescript
// Frontend: describe(<Component>) → it('<hành vi>')
describe('UserCard', () => {
  it('hiển thị tên người dùng')
  it('phát sự kiện edit khi nhấn nút chỉnh sửa')
  it('hiển thị skeleton khi đang tải')
})
```

---

## 8. Quy Tắc Bảo Mật

- Secrets KHÔNG BAO GIỜ trong code — chỉ biến môi trường
- `.env` trong `.gitignore` — `.env.example` commit vào git
- Passwords: bcrypt hash, KHÔNG plain text, KHÔNG MD5/SHA
- SQL: ORM queries hoặc parameterized `text()` — KHÔNG f-string SQL
- Frontend: KHÔNG `v-html` với user input, KHÔNG `eval()`, KHÔNG `innerHTML`
- JWT: verify signature + expiry ở backend — KHÔNG trust frontend
- File upload: validate MIME type + size limit — KHÔNG trust filename
- Logging: KHÔNG log passwords, tokens, PII — mask sensitive fields

---

## 9. Quy Tắc Hiệu Suất

### Backend
- `selectinload()` cho relationship collections — ngăn N+1
- Pagination mặc định — KHÔNG `SELECT *` không giới hạn
- Connection pool tuning: `pool_size=20`, `max_overflow=10`
- Redis cache cho data đọc nhiều, ít thay đổi
- Background tasks cho operations > 500ms (email, resize ảnh, v.v.)

### Frontend
- Route lazy loading — mọi page component dùng `() => import()`
- Component lazy loading cho component nặng — `defineAsyncComponent()`
- Image lazy loading — `loading="lazy"`
- Virtual scrolling cho danh sách > 100 items
- Debounce search input — 300ms
- Bundle < 200KB gzipped initial load

---

## 10. Quy Tắc Tài Liệu

- Cập nhật `CHANGELOG.md` sau MỌI tính năng/sửa lỗi
- Ghi `tasks/lessons.md` sau MỌI lần Claude bị sửa lỗi
- Ghi `tasks/decisions.md` cho MỌI quyết định kiến trúc
- README.md mỗi service cập nhật khi thêm endpoint/tính năng
- API docs tự động qua FastAPI OpenAPI — không viết tay
- Commit message là tài liệu — viết rõ ràng, đủ ngữ cảnh
