---
name: mau-api-gateway
description: Mẫu API Gateway với Nginx bao gồm reverse proxy, routing, CORS, SSL, rate limiting, và caching. Sử dụng khi cấu hình hoặc tối ưu API Gateway.
---

# Kỹ Năng Mẫu API Gateway

Cấu hình Nginx làm API Gateway cho hệ thống microservices.

## Nginx Config Hoàn Chỉnh

```nginx
# api_gateway/nginx.conf
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format JSON
    log_format json_combined escape=json
      '{"time":"$time_iso8601",'
       '"remote_addr":"$remote_addr",'
       '"method":"$request_method",'
       '"uri":"$request_uri",'
       '"status":$status,'
       '"body_bytes_sent":$body_bytes_sent,'
       '"request_time":$request_time,'
       '"upstream_response_time":"$upstream_response_time",'
       '"request_id":"$request_id"}';
    access_log /var/log/nginx/access.log json_combined;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 10m;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/css application/javascript application/json image/svg+xml;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_general:10m rate=30r/s;
    limit_req_zone $binary_remote_addr zone=api_auth:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api_upload:10m rate=10r/m;

    # Upstream backends
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;

        # Request ID propagation
        add_header X-Request-ID $request_id always;
        proxy_set_header X-Request-ID $request_id;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # ===== API Routes =====

        # Auth endpoints — rate limit nghiêm ngặt
        location /api/v1/auth/ {
            limit_req zone=api_auth burst=3 nodelay;
            include /etc/nginx/conf.d/proxy-common.conf;
            include /etc/nginx/conf.d/cors.conf;
            proxy_pass http://backend;
        }

        # Upload endpoints — rate limit riêng
        location /api/v1/upload {
            limit_req zone=api_upload burst=5;
            client_max_body_size 50m;
            include /etc/nginx/conf.d/proxy-common.conf;
            include /etc/nginx/conf.d/cors.conf;
            proxy_pass http://backend;
        }

        # General API — rate limit chung
        location /api/ {
            limit_req zone=api_general burst=50 nodelay;
            include /etc/nginx/conf.d/proxy-common.conf;
            include /etc/nginx/conf.d/cors.conf;
            proxy_pass http://backend;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # ===== Frontend Static Files =====
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;

            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
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
    }
}
```

```nginx
# api_gateway/conf.d/proxy-common.conf
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header Connection "";
proxy_connect_timeout 5s;
proxy_read_timeout 30s;
proxy_send_timeout 30s;
```

```nginx
# api_gateway/conf.d/cors.conf
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '$http_origin' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, PATCH, DELETE, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, X-Request-ID';
    add_header 'Access-Control-Allow-Credentials' 'true';
    add_header 'Access-Control-Max-Age' 86400;
    return 204;
}
add_header 'Access-Control-Allow-Origin' '$http_origin' always;
add_header 'Access-Control-Allow-Credentials' 'true';
```

## Bảng Kiểm Tra
- [ ] Reverse proxy cho tất cả API routes
- [ ] CORS chỉ ở Gateway (Backend không có CORSMiddleware)
- [ ] Rate limiting: 5/phút cho auth, 30/giây cho API chung
- [ ] Security headers đầy đủ
- [ ] Gzip compression enabled
- [ ] Request ID propagation
- [ ] JSON access logs
- [ ] WebSocket proxy (nếu cần)
- [ ] SPA fallback (try_files → index.html)
- [ ] Static asset caching (1 year, immutable)
- [ ] Health check endpoint
- [ ] Client body size limit
