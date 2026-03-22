# CLAUDE.md — Frontend (Vue 3)

## Vai Trò
Frontend SPA/SSR xử lý giao diện người dùng, routing client-side, quản lý trạng thái, và giao tiếp với Backend qua API Gateway.

## Quy Tắc
- Vue 3 Composition API: `<script setup lang="ts">` cho mọi component
- TypeScript strict: không `any`, không `@ts-ignore`
- Pinia cho quản lý trạng thái toàn cục
- Composables cho logic tái sử dụng (không mixins)
- TailwindCSS cho styling
- Vitest + Vue Test Utils cho testing
- Gọi API qua đường dẫn tương đối `/api/v1/` (Gateway proxy)
- KHÔNG gọi Backend trực tiếp (không dùng `http://localhost:8000`)
- Token lưu trong httpOnly cookie hoặc memory (không localStorage)
- KHÔNG dùng `v-html` với dữ liệu người dùng
- Mọi API call phải có loading, error, empty states

## Cấu Trúc
```
frontend/
├── src/
│   ├── components/
│   │   ├── base/            # BaseButton, BaseInput, BaseModal, BaseCard
│   │   ├── layout/          # AppHeader, AppSidebar, AppFooter
│   │   ├── shared/          # DataTable, Pagination, Alert, Toast
│   │   └── feature/         # Components theo tính năng
│   │       ├── auth/
│   │       └── dashboard/
│   ├── composables/         # useAuth, useApi, usePagination, useForm
│   ├── stores/              # Pinia stores
│   ├── pages/               # Route pages
│   ├── layouts/             # Layout wrappers
│   ├── router/              # Vue Router config + guards
│   ├── api/                 # HTTP client + typed endpoints
│   │   ├── client.ts        # Axios instance + interceptors
│   │   └── endpoints/
│   ├── types/               # TypeScript interfaces (khớp Backend schemas)
│   ├── utils/
│   └── assets/
├── tests/
│   ├── components/
│   ├── stores/
│   └── composables/
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── Dockerfile
```

## API Client Setup
```typescript
// src/api/client.ts
const apiClient = axios.create({
  baseURL: '/api/v1',  // ✅ Tương đối — Gateway sẽ proxy
  // baseURL: 'http://localhost:8000',  // ❌ KHÔNG BAO GIỜ
})
```

## Lệnh Phát Triển
```bash
# Trong Docker
docker compose exec frontend pnpm test
docker compose exec frontend pnpm build

# Local
cd frontend
pnpm install
pnpm dev          # Dev server port 3000
pnpm lint         # ESLint
pnpm type-check   # vue-tsc
pnpm test         # Vitest
pnpm build        # Production build
```
