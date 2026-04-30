export const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

type RequestOptions = {
  method?: string
  body?: unknown
  token?: string
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!response.ok) {
    const text = await response.text().catch(() => response.statusText)
    throw new ApiError(response.status, text)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export function setToken(token: string): void {
  localStorage.setItem('access_token', token)
}

export function clearToken(): void {
  localStorage.removeItem('access_token')
}

export async function authRequest<T>(path: string, options: Omit<RequestOptions, 'token'> = {}): Promise<T> {
  const token = getToken()
  try {
    return await request<T>(path, { ...options, token: token ?? undefined })
  } catch (err) {
    if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
      clearToken()
      window.location.href = '/login'
    }
    throw err
  }
}

export { request }
