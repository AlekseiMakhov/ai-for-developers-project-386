import { authRequest } from './client'
import type { Schedule, ScheduleCreate, ScheduleUpdate } from '@/types'

export function listSchedules(): Promise<Schedule[]> {
  return authRequest<Schedule[]>('/schedules')
}

export function createSchedule(payload: ScheduleCreate): Promise<Schedule> {
  return authRequest<Schedule>('/schedules', { method: 'POST', body: payload })
}

export function getSchedule(id: string): Promise<Schedule> {
  return authRequest<Schedule>(`/schedules/${id}`)
}

export function updateSchedule(id: string, payload: ScheduleUpdate): Promise<Schedule> {
  return authRequest<Schedule>(`/schedules/${id}`, { method: 'PUT', body: payload })
}

export function deleteSchedule(id: string): Promise<void> {
  return authRequest<void>(`/schedules/${id}`, { method: 'DELETE' })
}
