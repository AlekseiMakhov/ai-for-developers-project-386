<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useScheduleStore } from '@/stores/schedule'
import type { Schedule, ScheduleCreate, TimeRange, WeeklyAvailability } from '@/types'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Select from '@/components/ui/select/Select.vue'

const props = defineProps<{ schedule: Schedule | null }>()
const emit = defineEmits<{ done: []; cancel: [] }>()

const scheduleStore = useScheduleStore()
const { t, locale } = useI18n()

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#f97316']

const DURATION_OPTIONS = computed(() => [
  { value: '15', label: t('schedule.duration.d15') },
  { value: '30', label: t('schedule.duration.d30') },
  { value: '45', label: t('schedule.duration.d45') },
  { value: '60', label: t('schedule.duration.d60') },
  { value: '90', label: t('schedule.duration.d90') },
])

const DAY_KEYS: { key: keyof WeeklyAvailability; labelKey: string }[] = [
  { key: 'monday', labelKey: 'schedule.days.mon' },
  { key: 'tuesday', labelKey: 'schedule.days.tue' },
  { key: 'wednesday', labelKey: 'schedule.days.wed' },
  { key: 'thursday', labelKey: 'schedule.days.thu' },
  { key: 'friday', labelKey: 'schedule.days.fri' },
  { key: 'saturday', labelKey: 'schedule.days.sat' },
  { key: 'sunday', labelKey: 'schedule.days.sun' },
]

const DAYS = computed(() => DAY_KEYS.map((d) => ({ key: d.key, label: t(d.labelKey) })))

const is24h = computed(() => locale.value === 'ru')

function parseHhmm(hhmm: string): { h: number; m: number } {
  const [h = '9', m = '0'] = hhmm.split(':')
  return { h: parseInt(h), m: parseInt(m) }
}

function defaultState() {
  if (props.schedule) {
    const av = props.schedule.availability
    const activeDays = DAY_KEYS
      .filter((d) => (av[d.key]?.length ?? 0) > 0)
      .map((d) => d.key)
    const firstRange = Object.values(av).find((v): v is TimeRange[] => !!v && v.length > 0)?.[0]
    const start = parseHhmm(firstRange?.start ?? '09:00')
    const end = parseHhmm(firstRange?.end ?? '17:00')
    return {
      name: props.schedule.name,
      slug: props.schedule.slug,
      duration: String(props.schedule.duration),
      description: props.schedule.description ?? '',
      color: props.schedule.color ?? COLORS[0],
      activeDays,
      startH: start.h,
      startM: start.m,
      endH: end.h,
      endM: end.m,
    }
  }
  return {
    name: '',
    slug: '',
    duration: '30',
    description: '',
    color: COLORS[0],
    activeDays: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'] as (keyof WeeklyAvailability)[],
    startH: 9,
    startM: 0,
    endH: 17,
    endM: 0,
  }
}

const form = ref(defaultState())
const isLoading = ref(false)
const error = ref<string | null>(null)
const fieldErrors = ref<{ name: string | null; time: string | null }>({ name: null, time: null })

// 12h helpers
function to12(h24: number) { return h24 === 0 ? 12 : h24 > 12 ? h24 - 12 : h24 }
function getAmPm(h24: number): 'AM' | 'PM' { return h24 >= 12 ? 'PM' : 'AM' }
function to24(h12: number, ampm: 'AM' | 'PM') {
  if (ampm === 'AM') return h12 === 12 ? 0 : h12
  return h12 === 12 ? 12 : h12 + 12
}

function setHour(field: 'startH' | 'endH', raw: string) {
  const v = parseInt(raw) || 0
  if (is24h.value) {
    form.value[field] = Math.min(23, Math.max(0, v))
  } else {
    const ampm = getAmPm(form.value[field])
    form.value[field] = to24(Math.min(12, Math.max(1, v)), ampm)
  }
}

function setMin(field: 'startM' | 'endM', raw: string) {
  form.value[field] = Math.min(59, Math.max(0, parseInt(raw) || 0))
}

function toggleAmPm(field: 'startH' | 'endH') {
  const h = form.value[field]
  form.value[field] = h >= 12 ? h - 12 : h + 12
}

function fmt2(n: number) { return String(n).padStart(2, '0') }

function validate(): boolean {
  let valid = true
  if (!form.value.name.trim()) {
    fieldErrors.value.name = t('schedule.validation.nameRequired')
    valid = false
  } else {
    fieldErrors.value.name = null
  }
  const startTotal = form.value.startH * 60 + form.value.startM
  const endTotal = form.value.endH * 60 + form.value.endM
  if (startTotal >= endTotal) {
    fieldErrors.value.time = t('schedule.validation.timeOrder')
    valid = false
  } else {
    fieldErrors.value.time = null
  }
  return valid
}

watch(() => props.schedule, () => { form.value = defaultState() })

watch(() => form.value.name, (val) => {
  if (!props.schedule) {
    form.value.slug = val
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '')
  }
})

function toggleDay(key: keyof WeeklyAvailability) {
  const idx = form.value.activeDays.indexOf(key)
  if (idx === -1) form.value.activeDays.push(key)
  else form.value.activeDays.splice(idx, 1)
}

function buildAvailability(): WeeklyAvailability {
  const av: WeeklyAvailability = {}
  for (const day of DAY_KEYS) {
    av[day.key] = form.value.activeDays.includes(day.key)
      ? [{ start: `${fmt2(form.value.startH)}:${fmt2(form.value.startM)}`, end: `${fmt2(form.value.endH)}:${fmt2(form.value.endM)}` }]
      : []
  }
  return av
}

async function submit() {
  if (!validate()) return
  error.value = null
  isLoading.value = true
  try {
    const payload: ScheduleCreate = {
      name: form.value.name,
      slug: form.value.slug,
      duration: Number(form.value.duration),
      description: form.value.description || undefined,
      color: form.value.color,
      availability: buildAvailability(),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      isActive: true,
    }
    if (props.schedule) {
      await scheduleStore.update(props.schedule.id, payload)
    } else {
      await scheduleStore.create(payload)
    }
    emit('done')
  } catch {
    error.value = t('schedule.form.saveError')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <!-- Name -->
    <div class="space-y-1.5">
      <Label for="name">{{ t('schedule.form.name') }}</Label>
      <Input id="name" v-model="form.name" :placeholder="t('schedule.form.namePlaceholder')" maxlength="30" />
      <p v-if="fieldErrors.name" class="text-sm text-destructive">{{ fieldErrors.name }}</p>
    </div>

    <!-- Slug + Duration -->
    <div class="grid grid-cols-2 gap-3">
      <div class="space-y-1.5">
        <Label for="slug">{{ t('schedule.form.slug') }}</Label>
        <Input id="slug" v-model="form.slug" :placeholder="t('schedule.form.slugPlaceholder')" />
      </div>
      <div class="space-y-1.5">
        <Label for="duration">{{ t('schedule.form.duration') }}</Label>
        <Select id="duration" v-model="form.duration" :options="DURATION_OPTIONS" />
      </div>
    </div>

    <!-- Description -->
    <div class="space-y-1.5">
      <Label for="description">{{ t('schedule.form.description') }}</Label>
      <textarea
        id="description"
        v-model="form.description"
        :placeholder="t('schedule.form.descriptionPlaceholder')"
        rows="3"
        class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-base placeholder:text-muted-foreground focus-visible:outline-none resize-none"
      />
    </div>

    <!-- Color -->
    <div class="space-y-1.5">
      <Label>{{ t('schedule.form.color') }}</Label>
      <div class="flex gap-2.5">
        <button
          v-for="color in COLORS"
          :key="color"
          type="button"
          class="w-8 h-8 rounded-full focus:outline-none"
          :style="{
            backgroundColor: color,
            outline: form.color === color ? `3px solid ${color}` : 'none',
            outlineOffset: '2px',
          }"
          @click="form.color = color"
        />
      </div>
    </div>

    <!-- Days -->
    <div class="space-y-1.5">
      <Label>{{ t('schedule.form.days') }}</Label>
      <div class="flex gap-1.5 flex-wrap">
        <button
          v-for="day in DAYS"
          :key="day.key"
          type="button"
          class="px-3 py-1.5 rounded-md text-sm font-normal border transition-colors focus:outline-none"
          :class="
            form.activeDays.includes(day.key)
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-background text-foreground border-border hover:bg-secondary'
          "
          @click="toggleDay(day.key)"
        >
          {{ day.label }}
        </button>
      </div>
    </div>

    <!-- Time range -->
    <div class="grid grid-cols-2 gap-3">
      <!-- Start -->
      <div class="space-y-1.5">
        <Label>{{ t('schedule.form.startTime') }}</Label>
        <div class="time-field flex h-11 w-full items-center rounded-md border border-input bg-background px-3 gap-1 text-base">
          <input
            :value="is24h ? fmt2(form.startH) : fmt2(to12(form.startH))"
            type="number"
            :min="is24h ? 0 : 1"
            :max="is24h ? 23 : 12"
            class="time-digit w-7 bg-transparent text-center focus:outline-none"
            @change="setHour('startH', ($event.target as HTMLInputElement).value)"
          />
          <span class="text-muted-foreground select-none">:</span>
          <input
            :value="fmt2(form.startM)"
            type="number"
            min="0"
            max="59"
            class="time-digit w-7 bg-transparent text-center focus:outline-none"
            @change="setMin('startM', ($event.target as HTMLInputElement).value)"
          />
          <button
            v-if="!is24h"
            type="button"
            class="ml-1 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            @click="toggleAmPm('startH')"
          >
            {{ getAmPm(form.startH) }}
          </button>
        </div>
      </div>

      <!-- End -->
      <div class="space-y-1.5">
        <Label>{{ t('schedule.form.endTime') }}</Label>
        <div class="time-field flex h-11 w-full items-center rounded-md border border-input bg-background px-3 gap-1 text-base">
          <input
            :value="is24h ? fmt2(form.endH) : fmt2(to12(form.endH))"
            type="number"
            :min="is24h ? 0 : 1"
            :max="is24h ? 23 : 12"
            class="time-digit w-7 bg-transparent text-center focus:outline-none"
            @change="setHour('endH', ($event.target as HTMLInputElement).value)"
          />
          <span class="text-muted-foreground select-none">:</span>
          <input
            :value="fmt2(form.endM)"
            type="number"
            min="0"
            max="59"
            class="time-digit w-7 bg-transparent text-center focus:outline-none"
            @change="setMin('endM', ($event.target as HTMLInputElement).value)"
          />
          <button
            v-if="!is24h"
            type="button"
            class="ml-1 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            @click="toggleAmPm('endH')"
          >
            {{ getAmPm(form.endH) }}
          </button>
        </div>
      </div>
    </div>
    <p v-if="fieldErrors.time" class="text-sm text-destructive">{{ fieldErrors.time }}</p>

    <p v-if="error" class="text-base text-destructive">{{ error }}</p>

    <!-- Actions -->
    <div class="flex justify-end gap-2 pt-2">
      <Button type="button" variant="outline" @click="emit('cancel')">{{ t('common.cancel') }}</Button>
      <Button type="submit" :disabled="isLoading">
        {{ isLoading ? t('schedule.form.submitting') : (schedule ? t('schedule.form.submitSave') : t('schedule.form.submitCreate')) }}
      </Button>
    </div>
  </form>
</template>

<style scoped>
/* Hide number input spinners */
.time-digit::-webkit-inner-spin-button,
.time-digit::-webkit-outer-spin-button {
  appearance: none;
}
.time-digit {
  -moz-appearance: textfield;
}
</style>
