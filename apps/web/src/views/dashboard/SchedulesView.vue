<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useScheduleStore } from '@/stores/schedule'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/button/Button.vue'
import Dialog from '@/components/ui/dialog/Dialog.vue'
import ScheduleCard from '@/components/schedule/ScheduleCard.vue'
import ScheduleForm from '@/components/schedule/ScheduleForm.vue'
import { ApiError } from '@/api/client'
import type { Schedule } from '@/types'

const scheduleStore = useScheduleStore()
const authStore = useAuthStore()
const { t } = useI18n()

const showCreateDialog = ref(false)
const editingSchedule = ref<Schedule | null>(null)
const deletingSchedule = ref<Schedule | null>(null)
const blockedSchedule = ref<Schedule | null>(null)

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

function requestDelete(schedule: Schedule) {
  deletingSchedule.value = schedule
}

async function confirmDelete() {
  if (!deletingSchedule.value) return
  try {
    await scheduleStore.remove(deletingSchedule.value.id)
    deletingSchedule.value = null
  } catch (err) {
    if (err instanceof ApiError && err.status === 409) {
      blockedSchedule.value = deletingSchedule.value
      deletingSchedule.value = null
    } else {
      throw err
    }
  }
}

function closeDeleteDialog() {
  deletingSchedule.value = null
}
</script>

<template>
  <div>
    <!-- Page header -->
    <div class="flex items-start justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-foreground">{{ t('schedule.title') }}</h1>
        <p class="text-base text-muted-foreground mt-1">{{ t('schedule.subtitle') }}</p>
      </div>
      <Button @click="openCreate" class="gap-2">
        <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
        </svg>
        {{ t('schedule.newEvent') }}
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="scheduleStore.isLoading" class="text-muted-foreground text-base">{{ t('common.loading') }}</div>

    <!-- Empty state -->
    <div
      v-else-if="scheduleStore.schedules.length === 0"
      class="text-center py-16 text-muted-foreground"
    >
      <p class="text-xl font-medium">{{ t('schedule.noEvents') }}</p>
      <p class="text-base mt-1">{{ t('schedule.noEventsHint') }}</p>
    </div>

    <!-- Schedule grid -->
    <div v-else class="flex flex-wrap gap-4">
      <ScheduleCard
        v-for="schedule in scheduleStore.schedules"
        :key="schedule.id"
        :schedule="schedule"
        :user-slug="authStore.user?.slug ?? ''"
        @edit="openEdit(schedule)"
        @delete="requestDelete(schedule)"
        @toggle="scheduleStore.update(schedule.id, { isActive: !schedule.isActive })"
      />
    </div>
  </div>

  <!-- Create / Edit dialog -->
  <Dialog
    :open="showCreateDialog"
    :title="editingSchedule ? t('schedule.editTitle') : t('schedule.createTitle')"
    size="lg"
    @update:open="showCreateDialog = $event"
  >
    <ScheduleForm
      :schedule="editingSchedule"
      @done="onFormDone"
      @cancel="showCreateDialog = false"
    />
  </Dialog>

  <!-- Delete confirmation dialog -->
  <Dialog
    :open="!!deletingSchedule"
    :title="t('schedule.deleteTitle')"
    @update:open="closeDeleteDialog"
  >
    <div class="space-y-4">
      <p class="text-base text-foreground">
        {{ t('schedule.deleteConfirm', { name: deletingSchedule?.name }) }}
      </p>
      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="deletingSchedule = null">{{ t('common.cancel') }}</Button>
        <Button
          variant="destructive"
          data-testid="confirm-delete-btn"
          @click="confirmDelete"
        >
          {{ t('common.delete') }}
        </Button>
      </div>
    </div>
  </Dialog>

  <!-- Cannot delete: has bookings -->
  <Dialog
    :open="!!blockedSchedule"
    :title="t('schedule.cannotDeleteTitle')"
    @update:open="blockedSchedule = null"
  >
    <div class="space-y-4">
      <div class="flex gap-3 items-start">
        <svg
          class="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
          />
        </svg>
        <p class="text-base text-foreground">
          {{ t('schedule.cannotDeleteMsg', { name: blockedSchedule?.name }) }}
        </p>
      </div>
      <div class="flex justify-end">
        <Button @click="blockedSchedule = null">{{ t('common.ok') }}</Button>
      </div>
    </div>
  </Dialog>
</template>
