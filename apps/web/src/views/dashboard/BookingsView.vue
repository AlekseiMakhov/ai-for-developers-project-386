<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useBookingStore } from '@/stores/booking'
import type { Booking, BookingStatus } from '@/types'
import BookingCard from '@/components/booking/BookingCard.vue'
import BookingDialog from '@/components/booking/BookingDialog.vue'
import { useToast } from '@/composables/useToast'

const bookingStore = useBookingStore()
const toast = useToast()

const selectedBooking = ref<Booking | null>(null)
const dialogOpen = ref(false)
const activeFilter = ref<BookingStatus | 'all'>('all')

const filters: { label: string; value: BookingStatus | 'all' }[] = [
  { label: 'Все', value: 'all' },
  { label: 'Ожидают', value: 'pending' },
  { label: 'Подтверждены', value: 'confirmed' },
  { label: 'Отменены', value: 'cancelled' },
]

const filteredBookings = computed(() => {
  if (activeFilter.value === 'all') return bookingStore.bookings
  return bookingStore.bookings.filter((b) => b.status === activeFilter.value)
})

onMounted(() => bookingStore.fetchBookings())

function openDialog(booking: Booking) {
  selectedBooking.value = booking
  dialogOpen.value = true
}

async function onConfirm(id: string) {
  try {
    await bookingStore.confirmBooking(id)
    // refresh selectedBooking from store
    selectedBooking.value = bookingStore.bookings.find((b) => b.id === id) ?? null
    toast.show('Бронирование подтверждено')
  } catch {
    toast.show('Ошибка', 'Не удалось подтвердить бронирование')
  }
}

async function onCancel(id: string) {
  try {
    await bookingStore.cancelBooking(id)
    selectedBooking.value = bookingStore.bookings.find((b) => b.id === id) ?? null
    toast.show('Бронирование отменено')
  } catch {
    toast.show('Ошибка', 'Не удалось отменить бронирование')
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-foreground">Бронирования</h1>
      <p class="text-base text-muted-foreground mt-1">Управляйте входящими бронированиями</p>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-1 mb-4 flex-wrap">
      <button
        v-for="f in filters"
        :key="f.value"
        class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
        :class="
          activeFilter === f.value
            ? 'bg-secondary text-foreground'
            : 'text-muted-foreground hover:text-primary hover:bg-accent'
        "
        @click="activeFilter = f.value"
      >
        {{ f.label }}
        <span
          v-if="f.value !== 'all'"
          class="ml-1 text-xs opacity-60"
        >
          {{ bookingStore.bookings.filter((b) => b.status === f.value).length }}
        </span>
        <span v-else class="ml-1 text-xs opacity-60">{{ bookingStore.bookings.length }}</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="bookingStore.isLoading" class="text-muted-foreground text-base">Загрузка...</div>

    <!-- Empty state -->
    <div
      v-else-if="filteredBookings.length === 0"
      class="text-center py-16 text-muted-foreground"
      data-testid="empty-bookings"
    >
      <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-xl font-medium">Нет бронирований</p>
      <p class="text-base mt-1">
        {{ activeFilter === 'all' ? 'Поделитесь ссылкой на бронирование, чтобы получить первую запись' : 'Нет бронирований с таким статусом' }}
      </p>
    </div>

    <!-- Booking list -->
    <div v-else class="flex flex-col gap-2">
      <BookingCard
        v-for="booking in filteredBookings"
        :key="booking.id"
        :booking="booking"
        @click="openDialog(booking)"
      />
    </div>
  </div>

  <!-- Booking detail dialog -->
  <BookingDialog
    :open="dialogOpen"
    :booking="selectedBooking"
    @update:open="dialogOpen = $event"
    @confirm="onConfirm"
    @cancel="onCancel"
  />
</template>
