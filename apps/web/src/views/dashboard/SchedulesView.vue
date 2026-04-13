<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useScheduleStore } from '@/stores/schedule'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/button/Button.vue'
import Dialog from '@/components/ui/dialog/Dialog.vue'
import ScheduleCard from '@/components/schedule/ScheduleCard.vue'
import ScheduleForm from '@/components/schedule/ScheduleForm.vue'
import type { Schedule } from '@/types'

const scheduleStore = useScheduleStore()
const authStore = useAuthStore()

const showCreateDialog = ref(false)
const editingSchedule = ref<Schedule | null>(null)

onMounted(() => scheduleStore.fetchAll())

function openCreate() {
  editingSchedule.value = null
  showCreateDialog.value = true
}

function openEdit(schedule: Schedule) {
  editingSchedule.value = schedule
  showCreateDialog.value = true
}

async function onFormDone() {
  showCreateDialog.value = false
  editingSchedule.value = null
}
</script>

<template>
  <div>
    <!-- Page header -->
    <div class="flex items-start justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Типы событий</h1>
        <p class="text-base text-muted-foreground mt-1">
          Создавайте типы событий и делитесь ссылкой для бронирования
        </p>
      </div>
      <Button @click="openCreate" class="gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Новое событие
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="scheduleStore.isLoading" class="text-muted-foreground text-base">Загрузка...</div>

    <!-- Empty state -->
    <div
      v-else-if="scheduleStore.schedules.length === 0"
      class="text-center py-16 text-muted-foreground"
    >
      <p class="text-xl font-medium">Пока нет событий</p>
      <p class="text-base mt-1">Нажмите «Новое событие», чтобы создать первый тип</p>
    </div>

    <!-- Schedule grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <ScheduleCard
        v-for="schedule in scheduleStore.schedules"
        :key="schedule.id"
        :schedule="schedule"
        :user-slug="authStore.user?.slug ?? ''"
        @edit="openEdit(schedule)"
        @delete="scheduleStore.remove(schedule.id)"
        @toggle="scheduleStore.update(schedule.id, { isActive: !schedule.isActive })"
      />
    </div>
  </div>

  <!-- Create / Edit dialog -->
  <Dialog
    :open="showCreateDialog"
    :title="editingSchedule ? 'Редактировать событие' : 'Новое событие'"
    @update:open="showCreateDialog = $event"
  >
    <ScheduleForm
      :schedule="editingSchedule"
      @done="onFormDone"
      @cancel="showCreateDialog = false"
    />
  </Dialog>
</template>
