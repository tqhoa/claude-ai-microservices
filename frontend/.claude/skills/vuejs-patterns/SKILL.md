---
name: mau-vuejs
description: Mẫu Vue.js cho Frontend microservice. Component patterns, API integration.
---
# Mẫu Vue.js

## API Client (QUAN TRỌNG)
```typescript
// ✅ ĐÚNG: URL tương đối qua Gateway
const apiClient = axios.create({ baseURL: '/api/v1' })

// ❌ SAI: Gọi Backend trực tiếp
// const apiClient = axios.create({ baseURL: 'http://localhost:8000' })
```

## Interceptor Chuẩn
```typescript
// Request: gắn token
apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

// Response: xử lý lỗi chung
apiClient.interceptors.response.use(null, (error) => {
  if (error.response?.status === 401) {
    useAuthStore().logout()
    useRouter().push('/login')
  }
  return Promise.reject(error)
})
```

## Component Template Chuẩn
```vue
<script setup lang="ts">
const { data, loading, error, execute } = useAsyncData(() => usersApi.list())
onMounted(() => execute())
</script>

<template>
  <LoadingSkeleton v-if="loading" />
  <ErrorAlert v-else-if="error" :message="error" @retry="execute()" />
  <EmptyState v-else-if="!data?.length" />
  <UserList v-else :users="data" />
</template>
```
