<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { setToken } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  const token = route.query.token as string | undefined
  if (!token) {
    router.replace({ name: 'login' })
    return
  }
  setToken(token)
  try {
    await auth.fetchMe()
    router.replace('/dashboard')
  } catch {
    router.replace({ name: 'login' })
  }
})
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <svg class="w-8 h-8 animate-spin text-primary" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  </div>
</template>
