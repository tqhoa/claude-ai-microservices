# CLAUDE.md — Dự Án Microservices

## Tổng Quan Kiến Trúc

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend   │────▶│   API Gateway    │────▶│    Engine       │
│  (Vue 3)    │     │ (Nginx/Traefik)  │     │   (FastAPI)     │
│  Port 3000  │     │   Port 80/443    │     │   Port 8000     │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                              ┌────────┼────────┐
                                              │        │        │
                                           ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
                                           │ DB  │ │Redis│ │Queue│
                                           │5432 │ │6379 │ │5672 │
                                           └─────┘ └─────┘ └─────┘
```

## Cấu Trúc Dự Án

```
.
├── api_gateway/          # Nginx reverse proxy + rate limiting + SSL
├── engine/               # FastAPI async API + SQLAlchemy + Alembic
├── frontend/             # Vue 3 + Nuxt + Pinia + TailwindCSS
├── docker-compose.yml    # Orchestration tất cả services
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .github/workflows/    # CI/CD pipeline
├── docs/                 # Tài liệu kiến trúc
└── CLAUDE.md            # File này
```

---

### 1. Mặc Định Chế Độ Lập Kế Hoạch
- Vào chế độ lập kế hoạch cho BẤT KỲ tác vụ nào ảnh hưởng nhiều hơn 1 service
- Khi thay đổi API contract → lập kế hoạch cập nhật cả engine lẫn frontend
- Viết đặc tả chi tiết trước, đặc biệt cho giao tiếp giữa các service

### 2. Vòng Lặp Tự Cải Thiện
- Sau BẤT KỲ lần sửa lỗi: cập nhật `tasks/lessons.md`
- Ghi lại bài học về tương tác giữa các service (CORS, auth flow, API versioning)

### 3. Xác Minh Trước Khi Hoàn Thành
- Chạy `docker-compose up` và xác minh end-to-end flow
- Test từ frontend → API gateway → engine → database
- Kiểm tra CORS, auth token flow, error propagation

### 4. Kỹ Năng & Tác Nhân
- Mỗi thư mục con (api_gateway, engine, frontend) có `.claude/` riêng
- Kỹ năng ở thư mục gốc `.claude/skills/` áp dụng cho cross-cutting concerns
- Tải kỹ năng cụ thể cho từng service khi cần

### 5. Tác Nhân Phụ
- Dùng tác nhân phụ cho tác vụ chỉ liên quan 1 service
- Tác vụ cross-service giữ trong ngữ cảnh chính

## Nguyên Tắc Cốt Lõi
- **API-First**: Thiết kế API contract trước khi code
- **Đơn Giản Trước**: Mỗi service càng đơn giản càng tốt
- **Không Lười Biếng**: Tìm nguyên nhân gốc rễ, không sửa tạm
- **Tách Biệt Rõ Ràng**: Mỗi service có trách nhiệm riêng

## Hướng Dẫn Chung

### API Gateway (api_gateway/)
- Nginx làm reverse proxy
- Rate limiting và request throttling
- SSL termination
- CORS headers
- Request/response logging
- Health check endpoints
- Load balancing (nếu nhiều engine instances)

### Engine (engine/)
- Python 3.12+ với FastAPI
- `<script setup lang="ts">` tương đương: async/await xuyên suốt
- SQLAlchemy 2.0 async + Alembic migrations
- Pydantic v2 cho tất cả schemas
- pytest + pytest-asyncio cho testing
- structlog cho structured logging

### Frontend (frontend/)
- Vue 3 Composition API + TypeScript strict
- Nuxt 3 cho SSR/SSG (tùy chọn)
- Pinia cho quản lý trạng thái
- TailwindCSS cho styling
- Vitest + Vue Test Utils cho testing
- Axios/ofetch cho HTTP client

### Quy Tắc Chung
- Docker Compose cho development và production
- GitHub Actions cho CI/CD
- Semantic versioning cho mỗi service
- Biến môi trường qua `.env` files
- Không hard-code URLs giữa services
- API versioning (`/api/v1/`)
- Shared types/contracts giữa frontend và engine
- Structured logging JSON cho tất cả services

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **claude-ai-microservices** (229 symbols, 562 relationships, 19 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/claude-ai-microservices/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/claude-ai-microservices/context` | Codebase overview, check index freshness |
| `gitnexus://repo/claude-ai-microservices/clusters` | All functional areas |
| `gitnexus://repo/claude-ai-microservices/processes` | All execution flows |
| `gitnexus://repo/claude-ai-microservices/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## CLI

- Re-index: `npx gitnexus analyze`
- Check freshness: `npx gitnexus status`
- Generate docs: `npx gitnexus wiki`

<!-- gitnexus:end -->
