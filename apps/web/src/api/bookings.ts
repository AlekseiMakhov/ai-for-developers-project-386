import { request, authRequest } from './client'
import type { Booking, BookingCreate, HostsPage, PublicProfile, Schedule, Slot } from '@/types'

// ── Public (no auth) ──────────────────────────────────────────────────────────

export function getHosts(params?: {
  search?: string
  page?: number
  pageSize?: number
}): Promise<HostsPage> {
  const query = new URLSearchParams()
  if (params?.search) query.set('search', params.search)
  if (params?.page) query.set('page', String(params.page))
  if (params?.pageSize) query.set('page_size', String(params.pageSize))
  const qs = query.toString()
  return request<HostsPage>(`/public/hosts${qs ? `?${qs}` : ''}`)
}

export function getPublicProfile(slug: string): Promise<PublicProfile> {
  return request<PublicProfile>(`/public/${slug}`)
}

export function getPublicSchedule(slug: string, scheduleId: string): Promise<Schedule> {
  return request<Schedule>(`/public/${slug}/schedules/${scheduleId}`)
}

export function getSlotsForDate(slug: string, scheduleId: string, date: string): Promise<Slot[]> {
  return request<Slot[]>(`/public/${slug}/schedules/${scheduleId}/slots?date=${date}`)
}

export function getAvailableDates(slug: string, scheduleId: string): Promise<string[]> {
  return request<string[]>(`/public/${slug}/schedules/${scheduleId}/available-dates`)
}

export function createBooking(
  slug: string,
  scheduleId: string,
  payload: BookingCreate,
): Promise<Booking> {
  return request<Booking>(`/public/${slug}/schedules/${scheduleId}/bookings`, {
    method: 'POST',
    body: payload,
  })
}

export function guestConfirmBooking(token: string): Promise<Booking> {
  return request<Booking>(`/bookings/confirm/${token}`)
}

export function guestCancelBooking(token: string): Promise<Booking> {
  return request<Booking>(`/bookings/cancel/${token}`)
}

// ── Authenticated (host) ──────────────────────────────────────────────────────

export function listBookings(): Promise<Booking[]> {
  return authRequest<Booking[]>('/bookings')
}

export function getBooking(id: string): Promise<Booking> {
  return authRequest<Booking>(`/bookings/${id}`)
}

export function hostConfirmBooking(id: string): Promise<Booking> {
  return authRequest<Booking>(`/bookings/${id}/confirm`, { method: 'PATCH' })
}

export function hostCancelBooking(id: string): Promise<Booking> {
  return authRequest<Booking>(`/bookings/${id}/cancel`, { method: 'PATCH' })
}
