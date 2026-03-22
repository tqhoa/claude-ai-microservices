# Kỹ Năng (Skills) — Mức Hệ Thống

Kỹ năng ở cấp gốc dành cho cross-cutting concerns áp dụng cho toàn bộ hệ thống microservices.

## Kỹ Năng Có Sẵn

### Kiến Trúc & Orchestration
| Kỹ năng | Mô tả |
|---------|-------|
| [microservices-patterns](microservices-patterns/) | Mẫu giao tiếp, API contract, error propagation |
| [docker-orchestration](docker-orchestration/) | Docker Compose, multi-stage builds, health checks |
| [ci-cd-pipeline](ci-cd-pipeline/) | GitHub Actions multi-service, change detection |

### Cross-Cutting Concerns
| Kỹ năng | Mô tả |
|---------|-------|
| [api-gateway-patterns](api-gateway-patterns/) | Nginx reverse proxy, routing, CORS, SSL |
| [security-patterns](security-patterns/) | Auth flow, JWT, CORS, rate limiting xuyên services |
| [monitoring-observability](monitoring-observability/) | Logging, metrics, tracing xuyên services |
| [database-patterns](database-patterns/) | Migration, backup, connection pooling |
| [testing-strategy](testing-strategy/) | Test pyramid, E2E, contract testing |

### Kỹ Năng Theo Service
Mỗi service có kỹ năng riêng trong thư mục `.claude/skills/` của nó:
- `api_gateway/.claude/skills/` — Nginx, rate limiting, load balancing
- `backend/.claude/skills/` — FastAPI, SQLAlchemy, async patterns
- `frontend/.claude/skills/` — Vue.js, Pinia, component patterns
