<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BookingStatus } from '@/types'

const { status } = defineProps<{ status: BookingStatus }>()

const { t } = useI18n()

const labels = computed<Record<BookingStatus, string>>(() => ({
  pending: t('booking.status.pending'),
  confirmed: t('booking.status.confirmed'),
  cancelled: t('booking.status.cancelled'),
  past: t('booking.status.past'),
}))

const classes: Record<BookingStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  cancelled: 'bg-muted text-muted-foreground',
  past: 'bg-blue-100 text-blue-700',
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
