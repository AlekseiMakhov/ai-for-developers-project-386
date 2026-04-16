<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useBookingStore } from '@/stores/booking'
import Button from '@/components/ui/button/Button.vue'
import { getPublicSchedule } from '@/api/bookings'
import type { Schedule, Slot } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useBookingStore()
const { t, locale } = useI18n()

const slug = route.params.slug as string
const scheduleId = route.params.scheduleId as string

// Holds schedule fetched directly when it's not in the store (inactive schedules aren't returned by the profile endpoint)
const fetchedSchedule = ref<Schedule | null>(null)

// Calendar state
const today = new Date()

// Last selectable date: today + 13 (= 14 days total)
const windowEndDate = new Date(today)
windowEndDate.setDate(windowEndDate.getDate() + 13)
// Use local date components to avoid UTC-offset shifting (toISOString returns UTC)
function toLocalIso(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
const windowEndIso = toLocalIso(windowEndDate)

const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth()) // 0-indexed

const selectedDateStr = ref<string | null>(null)
const selectedSlot = ref<Slot | null>(null)

const schedule = computed(() =>
  fetchedSchedule.value ?? store.profile?.schedules.find((s) => s.id === scheduleId) ?? null,
)

const isScheduleInactive = computed(
  () => schedule.value !== null && !schedule.value.isActive,
)

onMounted(async () => {
  if (!store.profile) {
    await store.fetchProfile(slug)
  }
  // If schedule is not in the profile (e.g. inactive), fetch it directly so we can show the right state
  if (!store.profile?.schedules.find((s) => s.id === scheduleId)) {
    try {
      fetchedSchedule.value = await getPublicSchedule(slug, scheduleId)
    } catch {
      // schedule not found — leave null, template handles it
    }
    return
  }
  // Pre-fetch which dates have available slots for calendar coloring
  await store.fetchAvailableDates(slug, scheduleId)
})

// Calendar helpers
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  // Shift so week starts on Monday
  const startOffset = (firstDay + 6) % 7

  interface Cell {
    date: Date | null
    iso: string | null
    state: 'empty' | 'past' | 'unavailable' | 'no-slots' | 'has-slots' | 'beyond-window'
  }

  const cells: Cell[] = []

  for (let i = 0; i < startOffset; i++) {
    cells.push({ date: null, iso: null, state: 'empty' })
  }

  const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate())

  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, month, d)
    const iso = toLocalIso(date)

    let state: Cell['state']
    if (date < todayMidnight) {
      state = 'past'
    } else if (iso > windowEndIso) {
      state = 'beyond-window'
    } else if (store.availableDates === null) {
      // Still loading — treat as selectable (neutral)
      state = 'has-slots'
    } else if (store.availableDates.includes(iso)) {
      state = 'has-slots'
    } else {
      state = 'no-slots'
    }

    cells.push({ date, iso, state })
  }

  return cells
})

const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value, 1).toLocaleString(locale.value, {
    month: 'long',
    year: 'numeric',
  }),
)

// Disable prev-month button when the current month is today's month
const canGoPrev = computed(() => {
  return (
    currentYear.value > today.getFullYear() ||
    (currentYear.value === today.getFullYear() && currentMonth.value > today.getMonth())
  )
})

// Disable next-month button when showing the month containing windowEnd
const canGoNext = computed(() => {
  return (
    currentYear.value < windowEndDate.getFullYear() ||
    (currentYear.value === windowEndDate.getFullYear() &&
      currentMonth.value < windowEndDate.getMonth())
  )
})

function prevMonth() {
  if (!canGoPrev.value) return
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (!canGoNext.value) return
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

async function selectDate(iso: string) {
  selectedDateStr.value = iso
  selectedSlot.value = null
  await store.fetchSlots(slug, scheduleId, iso)
}

function pickSlot(slot: Slot) {
  if (slot.status !== 'available') return
  selectedSlot.value = slot
  store.selectedSlot = slot
}

function proceed() {
  if (!selectedSlot.value) return
  router.push({ name: 'public-booking-form', params: { slug, scheduleId } })
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString(locale.value, { hour: '2-digit', minute: '2-digit' })
}

// Available slots for the selected date (for "continue" button gating)
const availableSlotsForDate = computed(() =>
  store.dateSlots.filter((s) => s.status === 'available'),
)

const WEEKDAYS = computed(() => [
  t('schedule.days.mon'),
  t('schedule.days.tue'),
  t('schedule.days.wed'),
  t('schedule.days.thu'),
  t('schedule.days.fri'),
  t('schedule.days.sat'),
  t('schedule.days.sun'),
])
</script>

<template>
  <div class="py-8">
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      @click="router.push({ name: 'public-profile', params: { slug } })"
    >
      <svg class="w-5 h-5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
      </svg>
      {{ t('common.back') }}
    </button>

    <!-- Inactive schedule banner -->
    <div
      v-if="isScheduleInactive"
      class="flex flex-col items-center justify-center py-16 gap-4 text-center"
    >
      <svg
        class="w-12 h-12 text-yellow-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
        />
      </svg>
      <p class="text-xl font-semibold text-foreground">{{ t('public.slots.inactive') }}</p>
      <p v-if="schedule" class="text-base text-muted-foreground">{{ schedule.name }}</p>
    </div>

    <!-- Schedule info -->
    <div class="mb-6" v-else-if="schedule">
      <h1 class="text-2xl font-bold text-foreground">{{ schedule.name }}</h1>
      <p class="text-base text-muted-foreground mt-1">{{ schedule.duration }} {{ t('common.min') }} · {{ schedule.timezone }}</p>
    </div>

    <div v-if="!isScheduleInactive" class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Calendar -->
      <div>
        <!-- Month navigation -->
        <div class="flex items-center justify-between mb-4">
          <button
            class="p-1 rounded transition-colors"
            :class="canGoPrev ? 'hover:bg-secondary text-foreground' : 'text-muted-foreground/30 cursor-not-allowed'"
            :disabled="!canGoPrev"
            @click="prevMonth"
          >
            <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span class="text-base font-medium capitalize">{{ monthLabel }}</span>
          <button
            class="p-1 rounded transition-colors"
            :class="canGoNext ? 'hover:bg-secondary text-foreground' : 'text-muted-foreground/30 cursor-not-allowed'"
            :disabled="!canGoNext"
            @click="nextMonth"
          >
            <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- Legend -->
        <div class="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900"></span>
            {{ t('public.slots.legend.hasSlots') }}
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-red-200 dark:bg-red-900"></span>
            {{ t('public.slots.legend.noSlots') }}
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-muted"></span>
            {{ t('public.slots.legend.unavailable') }}
          </span>
        </div>

        <!-- Weekday headers -->
        <div class="grid grid-cols-7 mb-1">
          <div
            v-for="day in WEEKDAYS"
            :key="day"
            class="text-center text-xs font-medium text-muted-foreground py-1"
          >
            {{ day }}
          </div>
        </div>

        <!-- Day cells -->
        <div class="grid grid-cols-7 gap-1">
          <div v-for="(cell, i) in calendarDays" :key="i">
            <!-- Empty padding -->
            <div v-if="cell.state === 'empty'" />

            <!-- Selectable: has available slots -->
            <button
              v-else-if="cell.state === 'has-slots'"
              :class="[
                'w-full aspect-square rounded-md text-sm font-medium transition-colors',
                selectedDateStr === cell.iso
                  ? 'bg-primary text-primary-foreground ring-2 ring-primary ring-offset-1'
                  : 'bg-green-100 hover:bg-green-200 text-green-900 dark:bg-green-900/40 dark:hover:bg-green-900/60 dark:text-green-200',
              ]"
              @click="selectDate(cell.iso!)"
            >
              {{ cell.date!.getDate() }}
            </button>

            <!-- In window but no available slots: red, non-interactive -->
            <div
              v-else-if="cell.state === 'no-slots'"
              class="w-full aspect-square rounded-md text-sm font-medium bg-red-100 text-red-400 dark:bg-red-900/30 dark:text-red-500 flex items-center justify-center cursor-not-allowed select-none"
              :title="t('public.slots.noFreeSlots')"
            >
              {{ cell.date!.getDate() }}
            </div>

            <!-- Past / beyond 14-day window: grey -->
            <div
              v-else
              class="w-full aspect-square rounded-md text-sm text-muted-foreground/35 flex items-center justify-center select-none"
            >
              {{ cell.date!.getDate() }}
            </div>
          </div>
        </div>
      </div>

      <!-- Slot grid -->
      <div>
        <div v-if="!selectedDateStr" class="text-muted-foreground text-base pt-2">
          {{ t('public.slots.selectDate') }}
        </div>

        <div v-else-if="store.isLoading" class="text-muted-foreground text-base">
          {{ t('public.slots.loadingSlots') }}
        </div>

        <div v-else-if="store.dateSlots.length === 0" class="text-muted-foreground text-base">
          {{ t('public.slots.noSlots') }}
        </div>

        <div v-else>
          <p class="text-sm font-medium text-foreground mb-3">{{ t('public.slots.selectTime') }}</p>
          <div class="grid grid-cols-3 gap-2" data-testid="slot-grid">
            <Button
              v-for="slot in store.dateSlots"
              :key="slot.id"
              :disabled="slot.status !== 'available'"
              :variant="
                selectedSlot?.id === slot.id
                  ? 'default'
                  : slot.status !== 'available'
                    ? 'ghost'
                    : 'outline'
              "
              :class="[
                'text-sm',
                slot.status !== 'available'
                  ? 'opacity-40 cursor-not-allowed line-through'
                  : '',
              ]"
              :title="slot.status !== 'available' ? t('public.slots.slotBooked') : ''"
              @click="pickSlot(slot)"
            >
              {{ formatTime(slot.startAt) }}
            </Button>
          </div>

          <Button
            v-if="selectedSlot"
            class="w-full mt-6"
            @click="proceed"
          >
            {{ t('public.slots.proceed') }}
          </Button>

          <p
            v-else-if="availableSlotsForDate.length === 0"
            class="text-sm text-muted-foreground mt-3"
          >
            {{ t('public.slots.allBooked') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
