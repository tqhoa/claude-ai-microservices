# Quy Tắc Code — Frontend (Vue.js)

> Đọc rules gốc tại `../../.claude/rules/CODE_RULES.md` trước.
> File này bổ sung quy tắc RIÊNG cho Frontend.

---

## Cấm Tuyệt Đối (Vi phạm = revert ngay)

```vue
<!-- ❌ 1. Options API -->
<script>
export default { props: { user: Object } }
</script>

<!-- ❌ 2. v-html với user input -->
<div v-html="userComment"></div>

<!-- ❌ 3. Không typed props -->
<script setup lang="ts">
const props = defineProps({ name: String })  // THIẾU INTERFACE
</script>

<!-- ❌ 4. Gọi backend trực tiếp -->
<script setup lang="ts">
const { data } = await axios.get('http://localhost:8000/api/v1/users') // BYPASS GATEWAY
</script>
```

```typescript
// ❌ 5. localStorage cho token
localStorage.setItem('token', jwt)  // XSS CÓ THỂ ĐÁNH CẮP

// ❌ 6. any type
const data: any = await fetchData()  // MẤT TYPE SAFETY

// ❌ 7. console.log trong production
console.log('user:', user)  // XÓA TRƯỚC KHI COMMIT

// ❌ 8. Pinia options syntax
export const useStore = defineStore('store', {
  state: () => ({ count: 0 }),  // DÙNG SETUP SYNTAX
})
```

---

## Mẫu Đúng (Copy từ đây)

### Component chuẩn

```vue
<!-- components/feature/users/UserCard.vue -->
<script setup lang="ts">
import type { User } from '@/types'

interface Props {
  user: User
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  edit: [user: User]
  delete: [userId: number]
}>()
</script>

<template>
  <div class="rounded-lg border p-4">
    <h3 class="font-medium">{{ user.firstName }} {{ user.lastName }}</h3>
    <p class="text-sm text-gray-500">{{ user.email }}</p>
    <div v-if="editable" class="mt-3 flex gap-2">
      <button @click="emit('edit', user)">Sửa</button>
      <button @click="emit('delete', user.id)">Xóa</button>
    </div>
  </div>
</template>
```

### Page với đầy đủ states

```vue
<!-- pages/UsersPage.vue -->
<script setup lang="ts">
const { users, loading, error, fetchUsers } = useUsers()
onMounted(() => fetchUsers())
</script>

<template>
  <!-- Loading state -->
  <div v-if="loading" class="space-y-4">
    <UserCardSkeleton v-for="i in 5" :key="i" />
  </div>

  <!-- Error state -->
  <BaseAlert v-else-if="error" variant="danger" @action="fetchUsers()">
    {{ error }}
  </BaseAlert>

  <!-- Empty state -->
  <BaseEmpty v-else-if="users.length === 0" message="Chưa có người dùng nào" />

  <!-- Data state -->
  <div v-else class="space-y-4">
    <UserCard
      v-for="user in users"
      :key="user.id"
      :user="user"
      editable
      @edit="openEditModal"
      @delete="confirmDelete"
    />
  </div>
</template>
```

### Pinia store (setup syntax)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const fullName = computed(() =>
    user.value ? `${user.value.firstName} ${user.value.lastName}` : '',
  )

  async function login(credentials: LoginForm) {
    loading.value = true
    try {
      const { data } = await authApi.login(credentials)
      token.value = data.accessToken
      user.value = data.user
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    router.push({ name: 'login' })
  }

  return { user, token, loading, isAuthenticated, fullName, login, logout }
})
```

### API client

```typescript
// api/client.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',  // ← Tương đối, Gateway proxy
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token)
    config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

apiClient.interceptors.response.use(
  response => response,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      useAuthStore().logout()
    }
    else if (status === 403) {
      toast.error('Bạn không có quyền thực hiện thao tác này')
    }
    else if (status === 429) {
      toast.warning('Quá nhiều yêu cầu, vui lòng thử lại sau')
    }
    else if (status >= 500) {
      toast.error('Lỗi hệ thống, vui lòng thử lại')
    }
    return Promise.reject(error)
  },
)
```

### TypeScript types (khớp backend schemas)

```typescript
// types/user.ts — PHẢI khớp backend/app/schemas/user.py
export interface User {
  id: number
  email: string
  firstName: string   // camelCase — backend alias_generator chuyển đổi
  lastName: string
  role: 'user' | 'admin'
  isActive: boolean
  createdAt: string   // ISO 8601
}

export interface UserCreate {
  email: string
  firstName: string
  lastName: string
  password: string
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}
```

---

## Checklist Trước Khi Commit

```bash
pnpm lint                        # ESLint sạch
pnpm type-check                  # vue-tsc sạch
pnpm test                        # Vitest pass
pnpm build                       # Build thành công

# Kiểm tra vi phạm rules
grep -rn "export default {" src/ --include="*.vue"     # Phải trống (no Options API)
grep -rn "v-html" src/ --include="*.vue"               # Review từng cái
grep -rn "localhost:8000" src/                          # Phải trống
grep -rn ": any" src/ --include="*.ts" --include="*.vue"  # Phải trống
grep -rn "console\.\(log\|warn\)" src/ --include="*.ts" --include="*.vue"  # Phải trống
grep -rn "localStorage" src/ --include="*.ts"          # Review — không dùng cho token
```
