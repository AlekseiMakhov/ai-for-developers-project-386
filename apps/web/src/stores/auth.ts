import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as authApi from '@/api/auth'
import { setToken, clearToken } from '@/api/client'
import type { User, UserCreate, UserLogin } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = () => !!user.value

  async function fetchMe() {
    try {
      user.value = await authApi.getMe()
    } catch {
      user.value = null
      clearToken()
    }
  }

  async function register(payload: UserCreate) {
    isLoading.value = true
    error.value = null
    try {
      const { accessToken } = await authApi.register(payload)
      setToken(accessToken)
      await fetchMe()
      router.push('/dashboard')
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Registration failed'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function login(payload: UserLogin) {
    isLoading.value = true
    error.value = null
    try {
      const { accessToken } = await authApi.login(payload)
      setToken(accessToken)
      await fetchMe()
      router.push('/dashboard')
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Login failed'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearToken()
      user.value = null
      router.push('/login')
    }
  }

  return { user, isLoading, error, isAuthenticated, fetchMe, register, login, logout }
})
