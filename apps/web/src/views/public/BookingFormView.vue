<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { ApiError } from '@/api/client'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'

const route = useRoute()
const router = useRouter()
const store = useBookingStore()

const slug = route.params.slug as string
const scheduleId = route.params.scheduleId as string

const guestName = ref('')
const guestEmail = ref('')
const guestNote = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)

const schedule = computed(() =>
  store.profile?.schedules.find((s) => s.id === scheduleId) ?? null,
)

const slot = computed(() => store.selectedSlot)

function formatSlot(iso: string) {
  return new Date(iso).toLocaleString('ru', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Guard: if no slot selected, go back
if (!slot.value) {
  router.replace({ name: 'public-slots', params: { slug, scheduleId } })
}

async function submit() {
  if (!slot.value) return
  if (!guestName.value.trim() || !guestEmail.value.trim()) {
    error.value = 'Заполните имя и email'
    return
  }

  isSubmitting.value = true
  error.value = null

  try {
    await store.submitBooking(slug, scheduleId, {
      slotId: slot.value.id,
      guestName: guestName.value.trim(),
      guestEmail: guestEmail.value.trim(),
      guestNote: guestNote.value.trim() || undefined,
    })
    router.push({ name: 'public-booking-confirm', params: { slug, scheduleId } })
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.status === 409 ? 'Этот слот уже занят, выберите другое время' : 'Произошла ошибка, попробуйте снова'
    } else {
      error.value = 'Произошла ошибка, попробуйте снова'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto">
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      @click="router.push({ name: 'public-slots', params: { slug, scheduleId } })"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
      </svg>
      Назад
    </button>

    <!-- Summary -->
    <div class="rounded-lg border border-border bg-secondary/30 p-4 mb-6" v-if="schedule && slot">
      <p class="font-semibold text-foreground">{{ schedule.name }}</p>
      <p class="text-sm text-muted-foreground mt-1">
        {{ formatSlot(slot.startAt) }} · {{ schedule.duration }} мин
      </p>
    </div>

    <!-- Form -->
    <h1 class="text-xl font-bold text-foreground mb-6">Введите ваши данные</h1>

    <form class="space-y-4" @submit.prevent="submit">
      <div class="space-y-1.5">
        <Label for="guest-name">Ваше имя *</Label>
        <Input
          id="guest-name"
          v-model="guestName"
          placeholder="Иван Иванов"
          required
        />
      </div>

      <div class="space-y-1.5">
        <Label for="guest-email">Email *</Label>
        <Input
          id="guest-email"
          v-model="guestEmail"
          type="email"
          placeholder="ivan@example.com"
          required
        />
      </div>

      <div class="space-y-1.5">
        <Label for="guest-note">Примечание</Label>
        <Input
          id="guest-note"
          v-model="guestNote"
          placeholder="Опишите тему встречи (необязательно)"
        />
      </div>

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <Button type="submit" class="w-full" :disabled="isSubmitting">
        {{ isSubmitting ? 'Отправка...' : 'Записаться' }}
      </Button>
    </form>
  </div>
</template>
