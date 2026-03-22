# CLAUDE.md — API Gateway (Nginx)

## Vai Trò
API Gateway là điểm vào duy nhất cho tất cả request từ client. Xử lý:
- Reverse proxy routing (/api/* → Backend, /* → Frontend static)
- CORS headers (Backend KHÔNG cần CORSMiddleware)
- Rate limiting (auth: 5/phút, API chung: 30/giây)
- SSL termination (production)
- Security headers
- Request logging (JSON format)
- Request ID generation và propagation
- WebSocket proxy

## Quy Tắc
- KHÔNG có business logic ở Gateway
- KHÔNG modify response body từ Backend
- CORS chỉ cấu hình tại đây
- Mọi request phải có X-Request-ID
- Health check tại /health
- Log format JSON cho tất cả access logs
- Nginx config phải pass `nginx -t` validation

## Cấu Trúc
```
api_gateway/
├── Dockerfile
├── nginx.conf              # Config chính
├── conf.d/
│   ├── proxy-common.conf   # Proxy settings dùng chung
│   └── cors.conf           # CORS configuration
└── ssl/                    # SSL certificates (production)
```

## Lệnh Phát Triển
```bash
# Kiểm tra cú pháp nginx
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t

# Reload config không downtime
docker compose exec gateway nginx -s reload

# Xem log
docker compose logs -f gateway
```
