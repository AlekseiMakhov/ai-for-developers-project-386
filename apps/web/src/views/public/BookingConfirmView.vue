<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useBookingStore } from '@/stores/booking'
import { guestCancelBooking } from '@/api/bookings'
import { ApiError } from '@/api/client'
import type { Booking } from '@/types'

const props = defineProps<{
  cancelToken?: string
}>()

const store = useBookingStore()

const booking = ref<Booking | null>(store.createdBooking)
const pageStatus = ref<'created' | 'loading' | 'cancelled' | 'error'>('created')
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (props.cancelToken) {
    pageStatus.value = 'loading'
    try {
      booking.value = await guestCancelBooking(props.cancelToken)
      pageStatus.value = 'cancelled'
    } catch (e) {
      pageStatus.value = 'error'
      errorMsg.value = e instanceof ApiError ? e.message : 'Ошибка отмены'
    }
  }
})

function formatDateTime(iso?: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const statusLabel = computed(() => {
  if (!booking.value) return ''
  const map: Record<string, string> = { pending: 'Ожидает подтверждения', confirmed: 'Подтверждено', cancelled: 'Отменено' }
  return map[booking.value.status] ?? booking.value.status
})
</script>

<template>
  <div class="max-w-md mx-auto py-12 px-4">

    <!-- Loading -->
    <div v-if="pageStatus === 'loading'" class="text-center text-muted-foreground">
      Обработка...
    </div>

    <!-- Booking created — show full details -->
    <div v-else-if="pageStatus === 'created'">
      <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-1 text-center">Запись создана!</h1>
      <p class="text-sm text-muted-foreground text-center mb-6">Ожидайте подтверждения от организатора</p>

      <div class="rounded-lg border bg-card p-5 space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-muted-foreground">Тип события</span>
          <span class="font-medium">{{ booking?.scheduleName ?? '—' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">Дата и время</span>
          <span class="font-medium">{{ formatDateTime(booking?.slotStartAt) }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">Имя</span>
          <span class="font-medium">{{ booking?.guestName }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">Email</span>
          <span class="font-medium">{{ booking?.guestEmail }}</span>
        </div>
        <div v-if="booking?.guestNote" class="flex justify-between">
          <span class="text-muted-foreground">Заметка</span>
          <span class="font-medium">{{ booking.guestNote }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">Статус</span>
          <span class="font-medium">{{ statusLabel }}</span>
        </div>
      </div>
    </div>

    <!-- Cancelled -->
    <div v-else-if="pageStatus === 'cancelled'" class="text-center">
      <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Запись отменена</h1>
      <p class="text-base text-muted-foreground">Ваша запись успешно отменена.</p>
    </div>

    <!-- Error -->
    <div v-else-if="pageStatus === 'error'" class="text-center">
      <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 4a8 8 0 100 16A8 8 0 0012 4z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Ошибка</h1>
      <p class="text-base text-muted-foreground">{{ errorMsg }}</p>
    </div>

  </div>
</template>
