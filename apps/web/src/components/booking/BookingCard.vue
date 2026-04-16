<script setup lang="ts">
import type { Booking } from '@/types'
import BookingStatusBadge from './BookingStatusBadge.vue'

defineProps<{ booking: Booking }>()
const emit = defineEmits<{ click: [] }>()

function formatTime(iso: string | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div
    :class="[
      'border rounded-lg p-4 flex items-center gap-4 cursor-pointer transition-colors',
      booking.status === 'cancelled' || booking.status === 'past'
        ? 'bg-muted/60 border-border hover:border-border'
        : 'bg-card border-border hover:border-primary/50',
    ]"
    data-testid="booking-card"
    @click="emit('click')"
  >
    <!-- Date column -->
    <div class="flex-shrink-0 w-14 text-center">
      <p :class="['text-xl font-bold leading-none', booking.status === 'cancelled' || booking.status === 'past' ? 'text-muted-foreground' : 'text-foreground']">
        {{ booking.slotStartAt ? new Date(booking.slotStartAt).getDate() : '—' }}
      </p>
      <p class="text-xs text-muted-foreground mt-0.5 uppercase tracking-wide">
        {{
          booking.slotStartAt
            ? new Date(booking.slotStartAt).toLocaleDateString('ru-RU', { month: 'short' })
            : ''
        }}
      </p>
    </div>

    <!-- Divider -->
    <div class="w-px h-10 bg-border flex-shrink-0" />

    <!-- Main info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 min-w-0">
        <p :class="['font-semibold text-base truncate min-w-0', booking.status === 'cancelled' || booking.status === 'past' ? 'text-muted-foreground' : 'text-foreground']">{{ booking.guestName }}</p>
        <BookingStatusBadge :status="booking.status" class="shrink-0" />
      </div>
      <p class="text-sm text-muted-foreground truncate mt-0.5">{{ booking.guestEmail }}</p>
      <p v-if="booking.scheduleName" class="text-sm text-muted-foreground truncate mt-0.5">
        {{ booking.scheduleName }} &middot; {{ formatTime(booking.slotStartAt) }} – {{ formatTime(booking.slotEndAt) }}
      </p>
    </div>
  </div>
</template>
