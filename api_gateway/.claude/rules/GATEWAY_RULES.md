# Quy Tắc Code — API Gateway (Nginx)

> Đọc rules gốc tại `../../.claude/rules/CODE_RULES.md` trước.
> File này bổ sung quy tắc RIÊNG cho Gateway.

---

## Cấm Tuyệt Đối

```nginx
# ❌ 1. Proxy pass đến localhost (sẽ fail trong Docker)
proxy_pass http://localhost:8000;
# ✅ Dùng Docker service name
proxy_pass http://backend:8000;

# ❌ 2. Thiếu CORS cho API routes
location /api/ {
    proxy_pass http://backend:8000;  # THIẾU CORS HEADERS
}

# ❌ 3. Expose backend port ra ngoài Docker
# docker-compose.yml: backend ports: ["8000:8000"]  ← XÓA TRONG PROD

# ❌ 4. Hardcode secrets trong nginx.conf
ssl_certificate_key /etc/nginx/ssl/my-actual-key.pem;
```

---

## Mẫu Đúng

### Location blocks

```nginx
# Auth — rate limit nghiêm ngặt
location /api/v1/auth/ {
    limit_req zone=api_auth burst=3 nodelay;
    include /etc/nginx/conf.d/proxy-common.conf;
    include /etc/nginx/conf.d/cors.conf;
    proxy_pass http://backend:8000;
}

# API chung — rate limit bình thường
location /api/ {
    limit_req zone=api_general burst=50 nodelay;
    include /etc/nginx/conf.d/proxy-common.conf;
    include /etc/nginx/conf.d/cors.conf;
    proxy_pass http://backend:8000;
}

# Frontend SPA
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
    location ~* \.(js|css|png|jpg|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Health check
location /health {
    access_log off;
    return 200 'OK';
    add_header Content-Type text/plain;
}
```

### Bắt buộc trong mọi proxy location

```nginx
# conf.d/proxy-common.conf
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Request-ID $request_id;
proxy_set_header Connection "";
```

### Bắt buộc security headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## Checklist Trước Khi Commit

```bash
# Validate syntax
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t

# Kiểm tra
grep -n "localhost" nginx.conf conf.d/     # Phải trống (dùng service names)
grep -n "X-Request-ID" nginx.conf          # Phải có
grep -n "X-Frame-Options" nginx.conf       # Phải có
grep -c "cors" nginx.conf conf.d/          # Phải > 0
```
