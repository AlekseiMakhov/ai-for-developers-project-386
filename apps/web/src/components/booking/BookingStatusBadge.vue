<script setup lang="ts">
import type { BookingStatus } from '@/types'

defineProps<{ status: BookingStatus }>()

const labels: Record<BookingStatus, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждено',
  cancelled: 'Отменено',
}

const classes: Record<BookingStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  cancelled: 'bg-muted text-muted-foreground',
}
</script>

<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="classes[status]"
  >
    {{ labels[status] }}
  </span>
</template>
