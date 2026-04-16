<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBookingStore } from '@/stores/booking'
import { guestCancelBooking, guestConfirmBooking } from '@/api/bookings'
import { ApiError } from '@/api/client'
import type { Booking } from '@/types'

const props = defineProps<{
  cancelToken?: string
  confirmToken?: string
}>()

const store = useBookingStore()
const { t, locale } = useI18n()

const booking = ref<Booking | null>(store.createdBooking)
const pageStatus = ref<'created' | 'loading' | 'confirmed' | 'cancelled' | 'error'>('created')
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (props.confirmToken) {
    pageStatus.value = 'loading'
    try {
      booking.value = await guestConfirmBooking(props.confirmToken)
      pageStatus.value = 'confirmed'
    } catch (e) {
      pageStatus.value = 'error'
      errorMsg.value = e instanceof ApiError ? e.message : t('public.confirm.confirmError')
    }
  } else if (props.cancelToken) {
    pageStatus.value = 'loading'
    try {
      booking.value = await guestCancelBooking(props.cancelToken)
      pageStatus.value = 'cancelled'
    } catch (e) {
      pageStatus.value = 'error'
      errorMsg.value = e instanceof ApiError ? e.message : t('public.confirm.cancelError')
    }
  }
})

function formatDateTime(iso?: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(locale.value, {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const statusLabel = computed(() => {
  if (!booking.value) return ''
  const key = booking.value.status as 'pending' | 'confirmed' | 'cancelled'
  return t(`booking.statusLabel.${key}`, booking.value.status)
})
</script>

<template>
  <div class="max-w-md mx-auto py-12 px-4">

    <!-- Loading -->
    <div v-if="pageStatus === 'loading'" class="text-center text-muted-foreground">
      {{ t('public.confirm.processing') }}
    </div>

    <!-- Booking created — show full details -->
    <div v-else-if="pageStatus === 'created'">
      <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-1 text-center">{{ t('public.confirm.createdTitle') }}</h1>
      <p class="text-sm text-muted-foreground text-center mb-6">{{ t('public.confirm.createdSubtitle') }}</p>

      <div class="rounded-lg border bg-card p-5 space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('public.confirm.eventType') }}</span>
          <span class="font-medium">{{ booking?.scheduleName ?? '—' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('public.confirm.dateTime') }}</span>
          <span class="font-medium">{{ formatDateTime(booking?.slotStartAt) }}</span>
        </div>
        <div class="flex justify-between gap-2">
          <span class="text-muted-foreground shrink-0">{{ t('public.confirm.name') }}</span>
          <span class="font-medium truncate text-right">{{ booking?.guestName }}</span>
        </div>
        <div class="flex justify-between gap-2">
          <span class="text-muted-foreground shrink-0">{{ t('common.email') }}</span>
          <span class="font-medium truncate text-right">{{ booking?.guestEmail }}</span>
        </div>
        <div v-if="booking?.guestNote" class="flex justify-between gap-2">
          <span class="text-muted-foreground shrink-0">{{ t('public.confirm.note') }}</span>
          <span class="font-medium break-words min-w-0 text-right">{{ booking.guestNote }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('public.confirm.status') }}</span>
          <span class="font-medium">{{ statusLabel }}</span>
        </div>
      </div>
    </div>

    <!-- Confirmed via token -->
    <div v-else-if="pageStatus === 'confirmed'" class="text-center">
      <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">{{ t('public.confirm.confirmedTitle') }}</h1>
      <p class="text-base text-muted-foreground">{{ t('public.confirm.confirmedDesc') }}</p>
    </div>

    <!-- Cancelled -->
    <div v-else-if="pageStatus === 'cancelled'" class="text-center">
      <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">{{ t('public.confirm.cancelledTitle') }}</h1>
      <p class="text-base text-muted-foreground">{{ t('public.confirm.cancelledDesc') }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="pageStatus === 'error'" class="text-center">
      <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M12 4a8 8 0 100 16A8 8 0 0012 4z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">{{ t('public.confirm.errorTitle') }}</h1>
      <p class="text-base text-muted-foreground">{{ errorMsg }}</p>
    </div>

  </div>
</template>
