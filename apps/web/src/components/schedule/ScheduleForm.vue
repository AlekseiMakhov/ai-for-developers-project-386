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
const { t } = useI18n()

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

function defaultState() {
  if (props.schedule) {
    const av = props.schedule.availability
    const activeDays = DAY_KEYS
      .filter((d) => (av[d.key]?.length ?? 0) > 0)
      .map((d) => d.key)
    const firstRange = Object.values(av).find((v): v is TimeRange[] => !!v && v.length > 0)?.[0]
    return {
      name: props.schedule.name,
      slug: props.schedule.slug,
      duration: String(props.schedule.duration),
      description: props.schedule.description ?? '',
      color: props.schedule.color ?? COLORS[0],
      activeDays,
      startHour: firstRange?.start.split(':')[0] ?? '9',
      endHour: firstRange?.end.split(':')[0] ?? '17',
    }
  }
  return {
    name: '',
    slug: '',
    duration: '30',
    description: '',
    color: COLORS[0],
    activeDays: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'] as (keyof WeeklyAvailability)[],
    startHour: '9',
    endHour: '17',
  }
}

const form = ref(defaultState())
const isLoading = ref(false)
const error = ref<string | null>(null)
const fieldErrors = ref<{ name: string | null; hours: string | null }>({ name: null, hours: null })

function validate(): boolean {
  let valid = true
  if (!form.value.name.trim()) {
    fieldErrors.value.name = t('schedule.validation.nameRequired')
    valid = false
  } else {
    fieldErrors.value.name = null
  }
  if (Number(form.value.startHour) >= Number(form.value.endHour)) {
    fieldErrors.value.hours = t('schedule.validation.hoursOrder')
    valid = false
  } else {
    fieldErrors.value.hours = null
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
      ? [{ start: `${form.value.startHour.padStart(2, '0')}:00`, end: `${form.value.endHour.padStart(2, '0')}:00` }]
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
      <Input id="name" v-model="form.name" :placeholder="t('schedule.form.namePlaceholder')" />
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
        <Select
          id="duration"
          v-model="form.duration"
          :options="DURATION_OPTIONS"
        />
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
      <div class="flex gap-2">
        <button
          v-for="color in COLORS"
          :key="color"
          type="button"
          class="w-8 h-8 rounded-full border-2 transition-all focus:outline-none"
          :style="{ backgroundColor: color }"
          :class="form.color === color ? 'border-sky-500 border-[3px] scale-110' : 'border-transparent'"
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
      <div class="space-y-1.5">
        <Label for="start">{{ t('schedule.form.startHour') }}</Label>
        <Input id="start" v-model="form.startHour" type="number" min="0" max="23" placeholder="9" />
      </div>
      <div class="space-y-1.5">
        <Label for="end">{{ t('schedule.form.endHour') }}</Label>
        <Input id="end" v-model="form.endHour" type="number" min="1" max="24" placeholder="17" />
      </div>
    </div>
    <p v-if="fieldErrors.hours" class="text-sm text-destructive">{{ fieldErrors.hours }}</p>

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
