<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import Button from '@/components/ui/button/Button.vue'
import type { Slot } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useBookingStore()

const slug = route.params.slug as string
const scheduleId = route.params.scheduleId as string

// Calendar state
const today = new Date()

// Last selectable date: today + 13 (= 14 days total)
const windowEndDate = new Date(today)
windowEndDate.setDate(windowEndDate.getDate() + 13)
const windowEndIso = windowEndDate.toISOString().slice(0, 10)

const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth()) // 0-indexed

const selectedDateStr = ref<string | null>(null)
const selectedSlot = ref<Slot | null>(null)

const schedule = computed(() =>
  store.profile?.schedules.find((s) => s.id === scheduleId) ?? null,
)

onMounted(async () => {
  if (!store.profile) {
    await store.fetchProfile(slug)
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
    const iso = date.toISOString().slice(0, 10)

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
  new Date(currentYear.value, currentMonth.value, 1).toLocaleString('ru', {
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
  return new Date(iso).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
}

// Available slots for the selected date (for "continue" button gating)
const availableSlotsForDate = computed(() =>
  store.dateSlots.filter((s) => s.status === 'available'),
)

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
</script>

<template>
  <div>
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      @click="router.push({ name: 'public-profile', params: { slug } })"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
      </svg>
      Назад
    </button>

    <!-- Schedule info -->
    <div class="mb-6" v-if="schedule">
      <h1 class="text-2xl font-bold text-foreground">{{ schedule.name }}</h1>
      <p class="text-base text-muted-foreground mt-1">{{ schedule.duration }} мин · {{ schedule.timezone }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
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
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- Legend -->
        <div class="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900"></span>
            Есть слоты
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-red-200 dark:bg-red-900"></span>
            Нет слотов
          </span>
          <span class="flex items-center gap-1">
            <span class="inline-block w-3 h-3 rounded-sm bg-muted"></span>
            Недоступно
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
              :title="'Нет свободных слотов'"
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
          Выберите дату для просмотра слотов
        </div>

        <div v-else-if="store.isLoading" class="text-muted-foreground text-base">
          Загрузка слотов...
        </div>

        <div v-else-if="store.dateSlots.length === 0" class="text-muted-foreground text-base">
          Нет слотов на выбранную дату
        </div>

        <div v-else>
          <p class="text-sm font-medium text-foreground mb-3">Выберите время</p>
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
              :title="slot.status !== 'available' ? 'Занято' : ''"
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
            Продолжить
          </Button>

          <p
            v-else-if="availableSlotsForDate.length === 0"
            class="text-sm text-muted-foreground mt-3"
          >
            Все слоты на этот день уже заняты
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
