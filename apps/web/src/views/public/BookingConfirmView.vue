<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { guestConfirmBooking, guestCancelBooking } from '@/api/bookings'
import { ApiError } from '@/api/client'
import Button from '@/components/ui/button/Button.vue'
import type { Booking } from '@/types'

// Props are set by the router for token-based routes:
// /bookings/confirm/:token → { confirmToken }
// /bookings/cancel/:token  → { cancelToken }
const props = defineProps<{
  confirmToken?: string
  cancelToken?: string
}>()

const router = useRouter()
const store = useBookingStore()

const booking = ref<Booking | null>(store.createdBooking)
const pageStatus = ref<'pending' | 'loading' | 'confirmed' | 'cancelled' | 'error'>('pending')
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (props.confirmToken) {
    pageStatus.value = 'loading'
    try {
      booking.value = await guestConfirmBooking(props.confirmToken)
      pageStatus.value = 'confirmed'
    } catch (e) {
      pageStatus.value = 'error'
      errorMsg.value = e instanceof ApiError ? e.message : 'Ошибка подтверждения'
    }
  } else if (props.cancelToken) {
    pageStatus.value = 'loading'
    try {
      booking.value = await guestCancelBooking(props.cancelToken)
      pageStatus.value = 'cancelled'
    } catch (e) {
      pageStatus.value = 'error'
      errorMsg.value = e instanceof ApiError ? e.message : 'Ошибка отмены'
    }
  }
  // else: no token → just show "check your email" message (after form submit)
})

function goHome() {
  store.resetFlow()
  router.push('/')
}
</script>

<template>
  <div class="max-w-md mx-auto text-center py-12">

    <!-- Loading -->
    <div v-if="pageStatus === 'loading'" class="text-muted-foreground">
      Обработка...
    </div>

    <!-- After form submit — waiting for email confirmation -->
    <div v-else-if="pageStatus === 'pending'">
      <div class="w-16 h-16 rounded-full bg-yellow-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Почти готово!</h1>
      <p class="text-base text-muted-foreground">
        Мы отправили письмо на
        <strong>{{ booking?.guestEmail }}</strong>.
        Перейдите по ссылке в письме, чтобы подтвердить запись.
      </p>
      <Button class="mt-8" variant="outline" @click="goHome">На главную</Button>
    </div>

    <!-- Confirmed -->
    <div v-else-if="pageStatus === 'confirmed'">
      <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Запись подтверждена!</h1>
      <p class="text-base text-muted-foreground">
        Спасибо, {{ booking?.guestName }}! Ваша запись подтверждена.
      </p>
      <Button class="mt-8" variant="outline" @click="goHome">На главную</Button>
    </div>

    <!-- Cancelled -->
    <div v-else-if="pageStatus === 'cancelled'">
      <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Запись отменена</h1>
      <p class="text-base text-muted-foreground">Ваша запись успешно отменена.</p>
      <Button class="mt-8" variant="outline" @click="goHome">На главную</Button>
    </div>

    <!-- Error -->
    <div v-else-if="pageStatus === 'error'">
      <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 4a8 8 0 100 16A8 8 0 0012 4z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-3">Ошибка</h1>
      <p class="text-base text-muted-foreground">{{ errorMsg }}</p>
      <Button class="mt-8" variant="outline" @click="goHome">На главную</Button>
    </div>

  </div>
</template>
