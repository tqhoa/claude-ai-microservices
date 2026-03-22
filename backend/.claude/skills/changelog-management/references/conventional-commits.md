# Tham Khảo: Conventional Commits

## Format Commit Message

```
<loại>(<phạm vi>): <mô tả>

[thân commit]

[chân commit]
```

## Loại Commit → Tự Động Map Sang Changelog

| Commit type | Changelog section | Ví dụ |
|-------------|------------------|-------|
| `feat` | Thêm mới | `feat(users): thêm endpoint upload avatar` |
| `fix` | Sửa lỗi | `fix(auth): sửa lỗi refresh token hết hạn` |
| `perf` | Hiệu suất | `perf(db): thêm index cho users.email` |
| `refactor` | Nợ kỹ thuật | `refactor(services): tách UserService thành modules` |
| `docs` | — (không vào changelog) | `docs: cập nhật README` |
| `test` | — (không vào changelog) | `test(users): thêm test cho delete endpoint` |
| `chore` | — (không vào changelog) | `chore: update dependencies` |
| `security` | Bảo mật | `security(auth): thêm rate limiting cho login` |

## Breaking Changes

```
feat(api)!: đổi response format cho GET /users

BREAKING CHANGE: Response wrapper đổi từ `{items, total}` sang `{data, meta}`.
Frontend cần cập nhật type definitions.
```

## Phạm Vi (Scope)

| Scope | Mô tả |
|-------|-------|
| `auth` | Xác thực, JWT, permissions |
| `users` | User endpoints và logic |
| `db` | Database, migrations, queries |
| `api` | API contract, routing |
| `config` | Configuration, environment |
| `docker` | Dockerfile, docker-compose |
| `ci` | CI/CD pipeline |
| `deps` | Dependencies update |

## Script Tạo Changelog Từ Commits

```bash
# Liệt kê commits chưa release
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~50)..HEAD \
  | grep -E "^[a-f0-9]+ (feat|fix|perf|refactor|security)" \
  | sed 's/^[a-f0-9]* /- /'
```

## Git Hooks (Tự Động Validate)

```bash
# .git/hooks/commit-msg
#!/bin/sh
PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore|security)(\(.+\))?!?: .{1,72}"
if ! grep -qE "$PATTERN" "$1"; then
  echo "❌ Commit message không đúng format Conventional Commits"
  echo "Ví dụ: feat(users): thêm endpoint upload avatar"
  exit 1
fi
```
