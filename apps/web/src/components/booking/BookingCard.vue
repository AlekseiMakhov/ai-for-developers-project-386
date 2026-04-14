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
    class="bg-card border border-border rounded-lg p-4 flex items-center gap-4 cursor-pointer hover:border-primary/50 transition-colors"
    data-testid="booking-card"
    @click="emit('click')"
  >
    <!-- Date column -->
    <div class="flex-shrink-0 w-14 text-center">
      <p class="text-xl font-bold text-foreground leading-none">
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
      <div class="flex items-center gap-2 flex-wrap">
        <p class="font-semibold text-base text-foreground truncate">{{ booking.guestName }}</p>
        <BookingStatusBadge :status="booking.status" />
      </div>
      <p class="text-sm text-muted-foreground truncate mt-0.5">{{ booking.guestEmail }}</p>
      <p v-if="booking.scheduleName" class="text-sm text-muted-foreground mt-0.5">
        {{ booking.scheduleName }} &middot; {{ formatTime(booking.slotStartAt) }} – {{ formatTime(booking.slotEndAt) }}
      </p>
    </div>

    <!-- Arrow -->
    <svg class="w-5 h-5 text-muted-foreground flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
    </svg>
  </div>
</template>
