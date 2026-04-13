<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
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
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth()) // 0-indexed

const selectedDateStr = ref<string | null>(null)
const selectedSlot = ref<Slot | null>(null)

const schedule = computed(() =>
  store.profile?.schedules.find((s) => s.id === scheduleId) ?? null,
)

onMounted(async () => {
  // Load profile if not already in store
  if (!store.profile) {
    await store.fetchProfile(slug)
  }
})

// Calendar helpers
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month, 1).getDay() // 0=Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  // Shift so week starts on Monday (0=Mon)
  const startOffset = (firstDay + 6) % 7
  const cells: Array<{ date: Date | null; iso: string | null; isPast: boolean }> = []

  for (let i = 0; i < startOffset; i++) {
    cells.push({ date: null, iso: null, isPast: false })
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, month, d)
    const iso = date.toISOString().slice(0, 10)
    const isPast = date < new Date(today.getFullYear(), today.getMonth(), today.getDate())
    cells.push({ date, iso, isPast })
  }

  return cells
})

const monthLabel = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).toLocaleString('ru', {
    month: 'long',
    year: 'numeric',
  })
})

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

async function selectDate(iso: string | null) {
  if (!iso) return
  selectedDateStr.value = iso
  selectedSlot.value = null
  await store.fetchSlots(slug, scheduleId, iso)
}

function pickSlot(slot: Slot) {
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
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
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
        <div class="flex items-center justify-between mb-4">
          <button
            class="p-1 rounded hover:bg-secondary transition-colors"
            @click="prevMonth"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span class="text-base font-medium capitalize">{{ monthLabel }}</span>
          <button
            class="p-1 rounded hover:bg-secondary transition-colors"
            @click="nextMonth"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
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
          <div
            v-for="(cell, i) in calendarDays"
            :key="i"
          >
            <button
              v-if="cell.date && !cell.isPast"
              :class="[
                'w-full aspect-square rounded-md text-sm font-medium transition-colors',
                selectedDateStr === cell.iso
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary text-foreground',
              ]"
              @click="selectDate(cell.iso)"
            >
              {{ cell.date.getDate() }}
            </button>
            <div
              v-else-if="cell.date"
              class="w-full aspect-square rounded-md text-sm text-muted-foreground/40 flex items-center justify-center"
            >
              {{ cell.date.getDate() }}
            </div>
            <div v-else />
          </div>
        </div>
      </div>

      <!-- Slot grid -->
      <div>
        <div v-if="!selectedDateStr" class="text-muted-foreground text-base pt-2">
          Выберите дату для просмотра свободных слотов
        </div>

        <div v-else-if="store.isLoading" class="text-muted-foreground text-base">
          Загрузка слотов...
        </div>

        <div v-else-if="store.availableSlots.length === 0" class="text-muted-foreground text-base">
          Нет свободных слотов на выбранную дату
        </div>

        <div v-else>
          <p class="text-sm font-medium text-foreground mb-3">Выберите время</p>
          <div class="grid grid-cols-3 gap-2">
            <Button
              v-for="slot in store.availableSlots"
              :key="slot.id"
              :variant="selectedSlot?.id === slot.id ? 'default' : 'outline'"
              class="text-sm"
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
        </div>
      </div>
    </div>
  </div>
</template>
