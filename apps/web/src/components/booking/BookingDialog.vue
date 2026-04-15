<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Booking } from '@/types'
import Dialog from '@/components/ui/dialog/Dialog.vue'
import Button from '@/components/ui/button/Button.vue'
import BookingStatusBadge from './BookingStatusBadge.vue'

const props = defineProps<{
  open: boolean
  booking: Booking | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: [id: string]
  cancel: [id: string]
}>()

const { t, locale } = useI18n()

function formatDateTime(iso: string | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(locale.value, {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <Dialog
    :open="props.open"
    :title="booking?.guestName ?? t('booking.dialog.defaultTitle')"
    @update:open="emit('update:open', $event)"
  >
    <div v-if="booking" class="flex flex-col gap-4">
      <!-- Status -->
      <div class="flex items-center gap-2">
        <BookingStatusBadge :status="booking.status" />
      </div>

      <!-- Details -->
      <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
        <dt class="text-muted-foreground font-medium">{{ t('booking.dialog.guest') }}</dt>
        <dd class="text-foreground">{{ booking.guestName }}</dd>

        <dt class="text-muted-foreground font-medium">{{ t('common.email') }}</dt>
        <dd class="text-foreground break-all">{{ booking.guestEmail }}</dd>

        <template v-if="booking.scheduleName">
          <dt class="text-muted-foreground font-medium">{{ t('booking.dialog.eventType') }}</dt>
          <dd class="text-foreground">{{ booking.scheduleName }}</dd>
        </template>

        <template v-if="booking.slotStartAt">
          <dt class="text-muted-foreground font-medium">{{ t('booking.dialog.start') }}</dt>
          <dd class="text-foreground">{{ formatDateTime(booking.slotStartAt) }}</dd>
        </template>

        <template v-if="booking.slotEndAt">
          <dt class="text-muted-foreground font-medium">{{ t('booking.dialog.end') }}</dt>
          <dd class="text-foreground">{{ formatDateTime(booking.slotEndAt) }}</dd>
        </template>

        <template v-if="booking.guestNote">
          <dt class="text-muted-foreground font-medium">{{ t('booking.dialog.note') }}</dt>
          <dd class="text-foreground">{{ booking.guestNote }}</dd>
        </template>
      </dl>

      <!-- Actions -->
      <div v-if="booking.status === 'pending' || booking.status === 'confirmed'" class="flex gap-2 pt-2 border-t border-border">
        <Button
          v-if="booking.status === 'pending'"
          class="flex-1"
          data-testid="confirm-booking-btn"
          @click="emit('confirm', booking.id)"
        >
          {{ t('common.confirm') }}
        </Button>
        <Button
          variant="outline"
          class="flex-1"
          data-testid="cancel-booking-btn"
          @click="emit('cancel', booking.id)"
        >
          {{ t('common.cancel') }}
        </Button>
      </div>
    </div>
  </Dialog>
</template>
