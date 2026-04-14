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

async function shareLink() {
  if (navigator.share) {
    try {
      await navigator.share({
        title: props.schedule.name,
        text: `Запишитесь на ${props.schedule.name}`,
        url: publicUrl,
      })
    } catch {
      // user cancelled — do nothing
    }
  } else {
    // fallback: copy to clipboard
    navigator.clipboard.writeText(publicUrl)
    toast.show('Ссылка скопирована', publicUrl)
  }
}
</script>

<template>
  <div data-testid="schedule-card" class="relative bg-card border border-border rounded-lg overflow-hidden flex flex-col gap-4 p-5 transition-shadow hover:shadow-md w-full sm:w-[calc(50%-8px)] lg:w-[calc(33.333%-11px)] lg:min-w-[350px]">
    <!-- Left color bar -->
    <div
      class="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg"
      :style="{ backgroundColor: schedule.color ?? '#6366f1' }"
    />
    <!-- Header -->
    <div class="flex items-start justify-between gap-2">
      <div class="flex items-center gap-3 min-w-0">
        <div class="min-w-0">
          <p class="font-semibold text-base sm:text-base text-foreground truncate">{{ schedule.name }}</p>
          <p class="text-sm text-muted-foreground flex items-center gap-1.5 mt-1">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ schedule.duration }} мин
          </p>
        </div>
      </div>

      <!-- Toggle -->
      <button
        class="flex-shrink-0 w-9 h-5 rounded-full transition-colors relative"
        :class="schedule.isActive ? 'bg-primary' : 'bg-muted'"
        :title="schedule.isActive ? 'Деактивировать' : 'Активировать'"
        @click="emit('toggle')"
      >
        <span
          class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
          :class="schedule.isActive ? 'translate-x-4 left-0.5' : 'translate-x-0 left-0.5'"
        />
      </button>
    </div>

    <!-- Description -->
    <p v-if="schedule.description" class="text-sm text-muted-foreground line-clamp-1">
      {{ schedule.description }}
    </p>

    <!-- Actions -->
    <div class="flex items-center gap-1 pt-2 border-t border-border">
      <Button variant="ghost" class="h-11 w-11 p-0 lg:h-9 lg:w-auto lg:px-2.5 gap-1.5 text-sm" @click="copyLink">
        <svg class="w-7 h-7 flex-shrink-0 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <span class="hidden lg:inline">Копировать</span>
      </Button>
      <Button variant="ghost" class="h-11 w-11 p-0 lg:h-9 lg:w-auto lg:px-2.5 gap-1.5 text-sm" @click="shareLink">
        <svg class="w-7 h-7 flex-shrink-0 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        <span class="hidden lg:inline">Поделиться</span>
      </Button>
      <div class="ml-auto flex gap-1 flex-shrink-0">
        <Button variant="ghost" size="icon" class="w-11 h-11 lg:w-9 lg:h-9" @click="emit('edit')">
          <svg class="w-7 h-7 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </Button>
        <Button variant="ghost" size="icon" class="w-11 h-11 lg:w-9 lg:h-9 text-destructive hover:text-destructive" @click="emit('delete')">
          <svg class="w-7 h-7 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </Button>
      </div>
    </div>
  </div>
</template>
