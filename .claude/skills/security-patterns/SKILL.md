---
name: mau-bao-mat
description: Mẫu bảo mật xuyên microservices bao gồm JWT auth flow, CORS policy, SSL, rate limiting, và input validation. Sử dụng khi thiết lập hoặc đánh giá bảo mật hệ thống.
---

# Kỹ Năng Mẫu Bảo Mật

Bảo mật xuyên suốt API Gateway + Backend + Frontend.

## JWT Auth Flow Hoàn Chỉnh

```python
# backend/app/utils/security.py
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"])
ALGORITHM = "HS256"

def create_tokens(user_id: int, secret: str) -> dict:
    access = jwt.encode(
        {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(minutes=15)},
        secret, algorithm=ALGORITHM
    )
    refresh = jwt.encode(
        {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=7), "type": "refresh"},
        secret, algorithm=ALGORITHM
    )
    return {"access_token": access, "refresh_token": refresh}
```

```typescript
// frontend/src/stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  // Auto-refresh trước khi hết hạn
  let refreshTimer: ReturnType<typeof setTimeout> | null = null

  function scheduleRefresh(expiresIn: number) {
    if (refreshTimer) clearTimeout(refreshTimer)
    refreshTimer = setTimeout(async () => {
      await refreshAccessToken()
    }, (expiresIn - 60) * 1000) // Refresh 60s trước khi hết hạn
  }

  async function refreshAccessToken() {
    try {
      const { data } = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken.value,
      })
      token.value = data.access_token
      scheduleRefresh(data.expires_in)
    } catch {
      logout()
    }
  }
})
```

## Phân Bổ Trách Nhiệm

| Mối đe dọa | Gateway | Backend | Frontend |
|-------------|---------|---------|----------|
| DDoS | Rate limiting ✅ | — | — |
| XSS | CSP header ✅ | — | Không v-html ✅ |
| SQL Injection | — | ORM + Pydantic ✅ | — |
| CSRF | — | Token validation ✅ | Token gửi ✅ |
| Man-in-Middle | SSL/TLS ✅ | — | — |
| Brute force | Rate limit auth ✅ | Account lockout ✅ | — |
| Token theft | — | Short expiry ✅ | httpOnly cookie ✅ |
