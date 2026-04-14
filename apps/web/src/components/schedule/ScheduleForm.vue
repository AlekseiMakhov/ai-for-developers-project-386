<script setup lang="ts">
import { ref, watch } from 'vue'
import { useScheduleStore } from '@/stores/schedule'
import type { Schedule, WeeklyAvailability } from '@/types'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'

const props = defineProps<{ schedule: Schedule | null }>()
const emit = defineEmits<{ done: []; cancel: [] }>()

const scheduleStore = useScheduleStore()

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#f97316']
const DAYS = [
  { key: 'monday', label: 'Пн' },
  { key: 'tuesday', label: 'Вт' },
  { key: 'wednesday', label: 'Ср' },
  { key: 'thursday', label: 'Чт' },
  { key: 'friday', label: 'Пт' },
  { key: 'saturday', label: 'Сб' },
  { key: 'sunday', label: 'Вс' },
]

function defaultState() {
  if (props.schedule) {
    const av = props.schedule.availability
    const activeDays = DAYS.filter((d) => (av as any)[d.key]?.length > 0).map((d) => d.key)
    const foundRanges = Object.values(av as any).find((v: any) => v?.length > 0) as any[] | undefined
    const firstRange = foundRanges ? foundRanges[0] : undefined
    return {
      name: props.schedule.name,
      slug: props.schedule.slug,
      duration: String(props.schedule.duration),
      description: props.schedule.description ?? '',
      color: props.schedule.color ?? COLORS[0],
      activeDays,
      startHour: firstRange?.start?.split(':')[0] ?? '9',
      endHour: firstRange?.end?.split(':')[0] ?? '17',
    }
  }
  return {
    name: '',
    slug: '',
    duration: '30',
    description: '',
    color: COLORS[0],
    activeDays: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
    startHour: '9',
    endHour: '17',
  }
}

const form = ref(defaultState())
const isLoading = ref(false)
const error = ref<string | null>(null)

watch(() => props.schedule, () => { form.value = defaultState() })

watch(() => form.value.name, (val) => {
  if (!props.schedule) {
    form.value.slug = val
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '')
  }
})

function toggleDay(key: string) {
  const idx = form.value.activeDays.indexOf(key)
  if (idx === -1) form.value.activeDays.push(key)
  else form.value.activeDays.splice(idx, 1)
}

function buildAvailability(): WeeklyAvailability {
  const av: any = {}
  for (const day of DAYS) {
    av[day.key] = form.value.activeDays.includes(day.key)
      ? [{ start: `${form.value.startHour.padStart(2, '0')}:00`, end: `${form.value.endHour.padStart(2, '0')}:00` }]
      : []
  }
  return av
}

async function submit() {
  error.value = null
  isLoading.value = true
  try {
    const payload = {
      name: form.value.name,
      slug: form.value.slug,
      duration: Number(form.value.duration),
      description: form.value.description || undefined,
      color: form.value.color,
      bufferBefore: 0,
      bufferAfter: 0,
      availability: buildAvailability(),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      isActive: true,
    }
    if (props.schedule) {
      await scheduleStore.update(props.schedule.id, payload)
    } else {
      await scheduleStore.create(payload as any)
    }
    emit('done')
  } catch {
    error.value = 'Ошибка при сохранении. Попробуйте снова.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <!-- Name -->
    <div class="space-y-1.5">
      <Label for="name">Название *</Label>
      <Input id="name" v-model="form.name" placeholder="Консультация" required />
    </div>

    <!-- Slug + Duration -->
    <div class="grid grid-cols-2 gap-3">
      <div class="space-y-1.5">
        <Label for="slug">Slug</Label>
        <Input id="slug" v-model="form.slug" placeholder="konsultatsiya" />
      </div>
      <div class="space-y-1.5">
        <Label for="duration">Длительность (мин)</Label>
        <Input id="duration" v-model="form.duration" type="number" min="5" placeholder="30" />
      </div>
    </div>

    <!-- Description -->
    <div class="space-y-1.5">
      <Label for="description">Описание</Label>
      <textarea
        id="description"
        v-model="form.description"
        placeholder="Опишите событие..."
        rows="3"
        class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-base placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
      />
    </div>

    <!-- Color -->
    <div class="space-y-1.5">
      <Label>Цвет</Label>
      <div class="flex gap-2">
        <button
          v-for="color in COLORS"
          :key="color"
          type="button"
          class="w-8 h-8 rounded-full border-2 transition-all"
          :style="{ backgroundColor: color }"
          :class="form.color === color ? 'border-foreground scale-110' : 'border-transparent'"
          @click="form.color = color"
        />
      </div>
    </div>

    <!-- Days -->
    <div class="space-y-1.5">
      <Label>Дни приёма</Label>
      <div class="flex gap-1.5 flex-wrap">
        <button
          v-for="day in DAYS"
          :key="day.key"
          type="button"
          class="px-4 py-2 rounded-md text-base font-medium border transition-colors"
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
        <Label for="start">Начало (час)</Label>
        <Input id="start" v-model="form.startHour" type="number" min="0" max="23" placeholder="9" />
      </div>
      <div class="space-y-1.5">
        <Label for="end">Конец (час)</Label>
        <Input id="end" v-model="form.endHour" type="number" min="1" max="24" placeholder="17" />
      </div>
    </div>

    <p v-if="error" class="text-base text-destructive">{{ error }}</p>

    <!-- Actions -->
    <div class="flex justify-end gap-2 pt-2">
      <Button type="button" variant="outline" @click="emit('cancel')">Отмена</Button>
      <Button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Сохранение...' : (schedule ? 'Сохранить' : 'Создать') }}
      </Button>
    </div>
  </form>
</template>
