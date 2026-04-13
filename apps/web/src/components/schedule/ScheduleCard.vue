<script setup lang="ts">
import type { Schedule } from '@/types'
import Button from '@/components/ui/button/Button.vue'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  schedule: Schedule
  userSlug: string
}>()

const emit = defineEmits<{
  edit: []
  delete: []
  toggle: []
}>()

const publicUrl = `${window.location.origin}/book/${props.userSlug}/schedules/${props.schedule.id}/slots`
const toast = useToast()

function copyLink() {
  navigator.clipboard.writeText(publicUrl)
  toast.show('Ссылка скопирована', publicUrl)
}

function openPublicPage() {
  window.open(publicUrl, '_blank')
}
</script>

<template>
  <div class="relative bg-card border border-border rounded-lg p-5 sm:p-5 flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-start justify-between gap-2">
      <div class="flex items-center gap-3 min-w-0">
        <div
          class="w-1.5 h-12 rounded-full flex-shrink-0"
          :style="{ backgroundColor: schedule.color ?? '#6366f1' }"
        />
        <div class="min-w-0">
          <p class="font-semibold text-base sm:text-base text-foreground truncate">{{ schedule.name }}</p>
          <p class="text-sm text-muted-foreground flex items-center gap-1.5 mt-1">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ schedule.duration }} мин
          </p>
        </div>
      </div>

      <!-- Toggle -->
      <button
        class="flex-shrink-0 w-12 h-7 rounded-full transition-colors relative"
        :class="schedule.isActive ? 'bg-primary' : 'bg-muted'"
        @click="emit('toggle')"
      >
        <span
          class="absolute top-1 w-5 h-5 rounded-full bg-white shadow transition-transform"
          :class="schedule.isActive ? 'translate-x-5 left-1' : 'translate-x-0 left-1'"
        />
      </button>
    </div>

    <!-- Description -->
    <p v-if="schedule.description" class="text-sm text-muted-foreground line-clamp-2">
      {{ schedule.description }}
    </p>

    <!-- Actions -->
    <div class="flex items-center gap-1 pt-2 border-t border-border">
      <Button variant="ghost" size="sm" class="gap-2 text-sm h-9 px-3" @click="copyLink">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Копировать
      </Button>
      <Button variant="ghost" size="sm" class="gap-2 text-sm h-9 px-3" @click="openPublicPage">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        Открыть
      </Button>
      <div class="ml-auto flex gap-1">
        <Button variant="ghost" size="icon" class="w-9 h-9" @click="emit('edit')">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </Button>
        <Button variant="ghost" size="icon" class="w-9 h-9 text-destructive hover:text-destructive" @click="emit('delete')">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </Button>
      </div>
    </div>
  </div>
</template>
