import { test as base, expect } from '@playwright/test'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'

export interface TestUser {
  email: string
  name: string
  password: string
  slug: string
  token: string
}

export interface TestSchedule {
  id: string
  slug: string
}

export async function createUser(
  request: import('@playwright/test').APIRequestContext,
  overrides: Partial<TestUser> = {},
): Promise<TestUser> {
  const user = {
    email: `test-${Date.now()}@example.com`,
    name: 'Test User',
    password: 'password123',
    slug: `test-user-${Date.now()}`,
    timezone: 'UTC',
    ...overrides,
  }
  const res = await request.post(`${API_URL}/auth/register`, { data: user })
  const data = await res.json()
  return { ...user, token: data.accessToken }
}

export async function createSchedule(
  request: import('@playwright/test').APIRequestContext,
  token: string,
): Promise<TestSchedule> {
  const payload = {
    name: 'E2E Консультация',
    duration: 30,
    availability: {
      monday: [{ start: '09:00', end: '17:00' }],
      tuesday: [{ start: '09:00', end: '17:00' }],
      wednesday: [{ start: '09:00', end: '17:00' }],
      thursday: [{ start: '09:00', end: '17:00' }],
      friday: [{ start: '09:00', end: '17:00' }],
      saturday: [{ start: '09:00', end: '17:00' }],
      sunday: [{ start: '09:00', end: '17:00' }],
    },
    timezone: 'UTC',
    isActive: true,
    slug: `e2e-consult-${Date.now()}`,
  }
  const res = await request.post(`${API_URL}/schedules`, {
    data: payload,
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = await res.json()
  return { id: data.id, slug: data.slug }
}

export function getTomorrowISO(): string {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

export { base, expect }
