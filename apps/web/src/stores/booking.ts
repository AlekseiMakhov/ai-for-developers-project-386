import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as bookingsApi from '@/api/bookings'
import type { Booking, BookingCreate, PublicProfile, Slot } from '@/types'

const SESSION_KEY = 'createdBooking'

function loadBookingFromSession(): Booking | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as Booking) : null
  } catch {
    return null
  }
}

export const useBookingStore = defineStore('booking', () => {
  // Public booking flow state
  const profile = ref<PublicProfile | null>(null)
  const selectedScheduleId = ref<string | null>(null)
  const selectedDate = ref<string | null>(null)
  const availableDates = ref<string[] | null>(null)
  const dateSlots = ref<Slot[]>([])
  const selectedSlot = ref<Slot | null>(null)
  const createdBooking = ref<Booking | null>(loadBookingFromSession())

  // Host bookings
  const bookings = ref<Booking[]>([])
  const isLoading = ref(false)

  async function fetchProfile(slug: string) {
    isLoading.value = true
    try {
      profile.value = await bookingsApi.getPublicProfile(slug)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAvailableDates(slug: string, scheduleId: string) {
    try {
      availableDates.value = await bookingsApi.getAvailableDates(slug, scheduleId)
    } catch {
      availableDates.value = []
    }
  }

  async function fetchSlots(slug: string, scheduleId: string, date: string) {
    isLoading.value = true
    try {
      selectedScheduleId.value = scheduleId
      selectedDate.value = date
      dateSlots.value = await bookingsApi.getSlotsForDate(slug, scheduleId, date)
    } finally {
      isLoading.value = false
    }
  }

  async function submitBooking(slug: string, scheduleId: string, payload: BookingCreate): Promise<Booking> {
    const booking = await bookingsApi.createBooking(slug, scheduleId, payload)
    createdBooking.value = booking
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(booking))
    return booking
  }

  async function fetchBookings() {
    isLoading.value = true
    try {
      bookings.value = await bookingsApi.listBookings()
    } finally {
      isLoading.value = false
    }
  }

  async function confirmBooking(id: string) {
    const updated = await bookingsApi.hostConfirmBooking(id)
    const idx = bookings.value.findIndex((b) => b.id === id)
    if (idx !== -1) bookings.value[idx] = { ...bookings.value[idx], ...updated }
  }

  async function cancelBooking(id: string) {
    const updated = await bookingsApi.hostCancelBooking(id)
    const idx = bookings.value.findIndex((b) => b.id === id)
    if (idx !== -1) bookings.value[idx] = { ...bookings.value[idx], ...updated }
  }

  function resetFlow() {
    profile.value = null
    selectedScheduleId.value = null
    selectedDate.value = null
    availableDates.value = null
    dateSlots.value = []
    selectedSlot.value = null
    createdBooking.value = null
    sessionStorage.removeItem(SESSION_KEY)
  }

  return {
    profile,
    selectedScheduleId,
    selectedDate,
    availableDates,
    dateSlots,
    selectedSlot,
    createdBooking,
    bookings,
    isLoading,
    fetchProfile,
    fetchAvailableDates,
    fetchSlots,
    submitBooking,
    fetchBookings,
    confirmBooking,
    cancelBooking,
    resetFlow,
  }
})
