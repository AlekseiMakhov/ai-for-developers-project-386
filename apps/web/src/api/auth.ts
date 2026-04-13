import { request, authRequest } from './client'
import type { TokenResponse, User, UserCreate, UserLogin } from '@/types'

export function register(payload: UserCreate): Promise<TokenResponse> {
  return request<TokenResponse>('/auth/register', { method: 'POST', body: payload })
}

export function login(payload: UserLogin): Promise<TokenResponse> {
  return request<TokenResponse>('/auth/login', { method: 'POST', body: payload })
}

export function logout(): Promise<void> {
  return authRequest<void>('/auth/logout', { method: 'POST' })
}

export function getMe(): Promise<User> {
  return authRequest<User>('/auth/me')
}
