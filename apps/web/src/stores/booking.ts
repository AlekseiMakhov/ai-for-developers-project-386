import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as bookingsApi from '@/api/bookings'
import type { Booking, BookingCreate, PublicProfile, Slot } from '@/types'

export const useBookingStore = defineStore('booking', () => {
  // Public booking flow state
  const profile = ref<PublicProfile | null>(null)
  const selectedScheduleId = ref<string | null>(null)
  const selectedDate = ref<string | null>(null)
  const availableSlots = ref<Slot[]>([])
  const selectedSlot = ref<Slot | null>(null)
  const createdBooking = ref<Booking | null>(null)

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

  async function fetchSlots(slug: string, scheduleId: string, date: string) {
    isLoading.value = true
    try {
      selectedScheduleId.value = scheduleId
      selectedDate.value = date
      availableSlots.value = await bookingsApi.getAvailableSlots(slug, scheduleId, date)
    } finally {
      isLoading.value = false
    }
  }

  async function submitBooking(slug: string, scheduleId: string, payload: BookingCreate): Promise<Booking> {
    const booking = await bookingsApi.createBooking(slug, scheduleId, payload)
    createdBooking.value = booking
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

  function resetFlow() {
    profile.value = null
    selectedScheduleId.value = null
    selectedDate.value = null
    availableSlots.value = []
    selectedSlot.value = null
    createdBooking.value = null
  }

  return {
    profile,
    selectedScheduleId,
    selectedDate,
    availableSlots,
    selectedSlot,
    createdBooking,
    bookings,
    isLoading,
    fetchProfile,
    fetchSlots,
    submitBooking,
    fetchBookings,
    resetFlow,
  }
})
