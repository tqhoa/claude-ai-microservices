---
name: mau-nginx
description: Mẫu cấu hình Nginx cho API Gateway.
---
# Mẫu Nginx

Tham khảo đầy đủ: `../../../.claude/skills/api-gateway-patterns/SKILL.md`

## Tham Khảo Nhanh
- Proxy: `proxy_pass http://backend:8000;`
- CORS: Chỉ cấu hình tại Gateway
- Rate limit: `limit_req zone=api burst=50 nodelay;`
- SPA fallback: `try_files $uri $uri/ /index.html;`
- Health: `location /health { return 200 'OK'; }`
- WebSocket: `proxy_set_header Upgrade $http_upgrade;`
