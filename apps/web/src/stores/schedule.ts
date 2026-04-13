import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as schedulesApi from '@/api/schedules'
import type { Schedule, ScheduleCreate, ScheduleUpdate } from '@/types'

export const useScheduleStore = defineStore('schedule', () => {
  const schedules = ref<Schedule[]>([])
  const isLoading = ref(false)

  async function fetchAll() {
    isLoading.value = true
    try {
      schedules.value = await schedulesApi.listSchedules()
    } finally {
      isLoading.value = false
    }
  }

  async function create(payload: ScheduleCreate): Promise<Schedule> {
    const schedule = await schedulesApi.createSchedule(payload)
    schedules.value.push(schedule)
    return schedule
  }

  async function update(id: string, payload: ScheduleUpdate): Promise<Schedule> {
    const updated = await schedulesApi.updateSchedule(id, payload)
    const idx = schedules.value.findIndex((s) => s.id === id)
    if (idx !== -1) schedules.value[idx] = updated
    return updated
  }

  async function remove(id: string) {
    await schedulesApi.deleteSchedule(id)
    schedules.value = schedules.value.filter((s) => s.id !== id)
  }

  return { schedules, isLoading, fetchAll, create, update, remove }
})
