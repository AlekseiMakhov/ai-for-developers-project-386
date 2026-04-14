<script setup lang="ts">
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

function formatDateTime(iso: string | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', {
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
    :title="booking?.guestName ?? 'Бронирование'"
    @update:open="emit('update:open', $event)"
  >
    <div v-if="booking" class="flex flex-col gap-4">
      <!-- Status -->
      <div class="flex items-center gap-2">
        <BookingStatusBadge :status="booking.status" />
      </div>

      <!-- Details -->
      <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
        <dt class="text-muted-foreground font-medium">Гость</dt>
        <dd class="text-foreground">{{ booking.guestName }}</dd>

        <dt class="text-muted-foreground font-medium">Email</dt>
        <dd class="text-foreground break-all">{{ booking.guestEmail }}</dd>

        <template v-if="booking.scheduleName">
          <dt class="text-muted-foreground font-medium">Тип события</dt>
          <dd class="text-foreground">{{ booking.scheduleName }}</dd>
        </template>

        <template v-if="booking.slotStartAt">
          <dt class="text-muted-foreground font-medium">Начало</dt>
          <dd class="text-foreground">{{ formatDateTime(booking.slotStartAt) }}</dd>
        </template>

        <template v-if="booking.slotEndAt">
          <dt class="text-muted-foreground font-medium">Конец</dt>
          <dd class="text-foreground">{{ formatDateTime(booking.slotEndAt) }}</dd>
        </template>

        <template v-if="booking.guestNote">
          <dt class="text-muted-foreground font-medium">Заметка</dt>
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
          Подтвердить
        </Button>
        <Button
          variant="outline"
          class="flex-1"
          data-testid="cancel-booking-btn"
          @click="emit('cancel', booking.id)"
        >
          Отменить
        </Button>
      </div>
    </div>
  </Dialog>
</template>
