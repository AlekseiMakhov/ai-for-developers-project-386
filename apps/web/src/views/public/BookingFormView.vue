<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useBookingStore } from '@/stores/booking'
import { ApiError } from '@/api/client'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'

const route = useRoute()
const router = useRouter()
const store = useBookingStore()
const { t, locale } = useI18n()

const slug = route.params.slug as string
const scheduleId = route.params.scheduleId as string

const guestName = ref('')
const guestEmail = ref('')
const guestNote = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const fieldErrors = ref<{ name: string | null; email: string | null }>({ name: null, email: null })

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(): boolean {
  let valid = true
  if (!guestName.value.trim()) {
    fieldErrors.value.name = t('public.bookingForm.nameRequired')
    valid = false
  } else {
    fieldErrors.value.name = null
  }
  if (!guestEmail.value.trim()) {
    fieldErrors.value.email = t('public.bookingForm.emailRequired')
    valid = false
  } else if (!EMAIL_RE.test(guestEmail.value.trim())) {
    fieldErrors.value.email = t('public.bookingForm.emailInvalid')
    valid = false
  } else {
    fieldErrors.value.email = null
  }
  return valid
}

const schedule = computed(() =>
  store.profile?.schedules.find((s) => s.id === scheduleId) ?? null,
)

const slot = computed(() => store.selectedSlot)

function formatSlot(iso: string) {
  return new Date(iso).toLocaleString(locale.value, {
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
  if (!validate()) return

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
      error.value = e.status === 409
        ? t('public.bookingForm.conflictError')
        : t('public.bookingForm.genericError')
    } else {
      error.value = t('public.bookingForm.genericError')
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
      {{ t('common.back') }}
    </button>

    <!-- Summary -->
    <div class="rounded-lg border border-border bg-secondary/30 p-4 mb-6" v-if="schedule && slot">
      <p class="font-semibold text-foreground">{{ schedule.name }}</p>
      <p class="text-sm text-muted-foreground mt-1">
        {{ formatSlot(slot.startAt) }} · {{ schedule.duration }} {{ t('common.min') }}
      </p>
    </div>

    <!-- Form -->
    <h1 class="text-xl font-bold text-foreground mb-6">{{ t('public.bookingForm.title') }}</h1>

    <form class="space-y-4" @submit.prevent="submit">
      <div class="space-y-1.5">
        <Label for="guest-name">{{ t('public.bookingForm.guestName') }}</Label>
        <Input
          id="guest-name"
          v-model="guestName"
          :placeholder="t('public.bookingForm.guestNamePlaceholder')"
        />
        <p v-if="fieldErrors.name" class="text-sm text-destructive">{{ fieldErrors.name }}</p>
      </div>

      <div class="space-y-1.5">
        <Label for="guest-email">{{ t('common.email') }} *</Label>
        <Input
          id="guest-email"
          v-model="guestEmail"
          type="email"
          placeholder="ivan@example.com"
        />
        <p v-if="fieldErrors.email" class="text-sm text-destructive">{{ fieldErrors.email }}</p>
      </div>

      <div class="space-y-1.5">
        <Label for="guest-note">{{ t('public.bookingForm.guestNote') }}</Label>
        <Input
          id="guest-note"
          v-model="guestNote"
          :placeholder="t('public.bookingForm.guestNotePlaceholder')"
        />
      </div>

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <Button type="submit" class="w-full" :disabled="isSubmitting">
        {{ isSubmitting ? t('public.bookingForm.submitting') : t('public.bookingForm.submitBtn') }}
      </Button>
    </form>
  </div>
</template>
