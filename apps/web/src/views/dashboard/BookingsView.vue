<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBookingStore } from '@/stores/booking'
import type { Booking, BookingStatus } from '@/types'
import BookingCard from '@/components/booking/BookingCard.vue'
import BookingDialog from '@/components/booking/BookingDialog.vue'
import Dialog from '@/components/ui/dialog/Dialog.vue'
import Button from '@/components/ui/button/Button.vue'
import { useToast } from '@/composables/useToast'

const bookingStore = useBookingStore()
const toast = useToast()
const { t } = useI18n()

const selectedBooking = ref<Booking | null>(null)
const dialogOpen = ref(false)
const cancellingBooking = ref<Booking | null>(null)
const activeFilter = ref<BookingStatus>('confirmed')

const filters = computed<{ label: string; value: BookingStatus }[]>(() => [
  { label: t('booking.filters.pending'), value: 'pending' },
  { label: t('booking.filters.confirmed'), value: 'confirmed' },
  { label: t('booking.filters.past'), value: 'past' },
  { label: t('booking.filters.cancelled'), value: 'cancelled' },
])

const statusTextColor: Record<BookingStatus, string> = {
  pending: 'text-yellow-700',
  confirmed: 'text-green-700',
  cancelled: 'text-muted-foreground',
  past: 'text-blue-700',
}

const filteredBookings = computed(() =>
  bookingStore.bookings.filter((b) => b.status === activeFilter.value),
)

onMounted(() => bookingStore.fetchBookings())

function openDialog(booking: Booking) {
  selectedBooking.value = booking
  dialogOpen.value = true
}

async function onConfirm(id: string) {
  try {
    await bookingStore.confirmBooking(id)
    dialogOpen.value = false
    toast.show(t('booking.toast.confirmed'))
  } catch {
    toast.show(t('common.error'), t('booking.toast.confirmError'))
  }
}

function onCancel(id: string) {
  cancellingBooking.value = bookingStore.bookings.find((b) => b.id === id) ?? null
  dialogOpen.value = false
}

async function confirmCancel() {
  if (!cancellingBooking.value) return
  try {
    await bookingStore.cancelBooking(cancellingBooking.value.id)
    toast.show(t('booking.toast.cancelled'))
  } catch {
    toast.show(t('common.error'), t('booking.toast.cancelError'))
  } finally {
    cancellingBooking.value = null
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-foreground">{{ t('booking.title') }}</h1>
      <p class="text-base text-muted-foreground mt-1">{{ t('booking.subtitle') }}</p>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-1 mb-4 flex-wrap">
      <button
        v-for="f in filters"
        :key="f.value"
        class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
        :class="
          activeFilter === f.value
            ? ['bg-secondary', statusTextColor[f.value]]
            : 'text-muted-foreground hover:text-primary hover:bg-accent'
        "
        @click="activeFilter = f.value"
      >
        {{ f.label }}
        <span class="ml-1 text-xs opacity-60">
          {{ bookingStore.bookings.filter((b) => b.status === f.value).length }}
        </span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="bookingStore.isLoading" class="text-muted-foreground text-base">{{ t('common.loading') }}</div>

    <!-- Empty state -->
    <div
      v-else-if="filteredBookings.length === 0"
      class="text-center py-16 text-muted-foreground"
      data-testid="empty-bookings"
    >
      <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-xl font-medium">{{ t('booking.noBookings') }}</p>
      <p class="text-base mt-1">{{ t('booking.noBookingsStatus') }}</p>
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

  <!-- Cancel confirmation dialog -->
  <Dialog
    :open="!!cancellingBooking"
    :title="t('booking.cancelTitle')"
    @update:open="cancellingBooking = null"
  >
    <div class="space-y-4">
      <p class="text-base text-foreground">
        {{ t('booking.cancelConfirm', { name: cancellingBooking?.guestName }) }}
      </p>
      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="cancellingBooking = null">{{ t('common.back') }}</Button>
        <Button variant="destructive" @click="confirmCancel">{{ t('booking.cancelBtn') }}</Button>
      </div>
    </div>
  </Dialog>
</template>
