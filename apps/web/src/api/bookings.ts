import { request, authRequest } from './client'
import type { Booking, BookingCreate, PublicProfile, Slot } from '@/types'

// ── Public (no auth) ──────────────────────────────────────────────────────────

export function getPublicProfile(slug: string): Promise<PublicProfile> {
  return request<PublicProfile>(`/public/${slug}`)
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
