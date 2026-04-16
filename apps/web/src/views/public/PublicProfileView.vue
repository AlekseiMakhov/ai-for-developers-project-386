<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useBookingStore } from '@/stores/booking'
import Card from '@/components/ui/card/Card.vue'
import CardHeader from '@/components/ui/card/CardHeader.vue'
import CardTitle from '@/components/ui/card/CardTitle.vue'
import CardContent from '@/components/ui/card/CardContent.vue'
import CardDescription from '@/components/ui/card/CardDescription.vue'
import Button from '@/components/ui/button/Button.vue'

const route = useRoute()
const router = useRouter()
const store = useBookingStore()
const { t } = useI18n()

const slug = route.params.slug as string
const navigatingId = ref<string | null>(null)

onMounted(() => store.fetchProfile(slug))

async function selectSchedule(scheduleId: string) {
  if (navigatingId.value) return
  navigatingId.value = scheduleId
  try {
    await router.push({ name: 'public-slots', params: { slug, scheduleId } })
  } finally {
    navigatingId.value = null
  }
}
</script>

<template>
  <div class="py-8">
  <div v-if="store.isLoading && !store.profile" class="text-muted-foreground text-base">{{ t('common.loading') }}</div>

  <div v-else-if="store.profile">
    <!-- Host info -->
    <div class="mb-8 text-center">
      <div class="w-16 h-16 rounded-full bg-primary flex items-center justify-center mx-auto mb-3">
        <span class="text-primary-foreground text-2xl font-bold">
          {{ store.profile.user.name.charAt(0).toUpperCase() }}
        </span>
      </div>
      <h1 class="text-2xl font-bold text-foreground">{{ store.profile.user.name }}</h1>
      <p class="text-base text-muted-foreground mt-1">{{ store.profile.user.timezone }}</p>
    </div>

    <!-- Empty state -->
    <div
      v-if="store.profile.schedules.length === 0"
      class="text-center py-12 text-muted-foreground"
    >
      <p class="text-lg font-medium">{{ t('public.profile.noSchedules') }}</p>
    </div>

    <!-- Schedule list -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Card
        v-for="schedule in store.profile.schedules"
        :key="schedule.id"
        class="cursor-pointer hover:border-primary transition-colors"
        @click="selectSchedule(schedule.id)"
      >
        <CardHeader class="pb-2">
          <div class="flex items-center gap-3">
            <div
              class="w-3 h-3 rounded-full flex-shrink-0"
              :style="{ backgroundColor: schedule.color || '#6366f1' }"
            />
            <CardTitle class="text-lg">{{ schedule.name }}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription v-if="schedule.description" class="text-base mb-3">
            {{ schedule.description }}
          </CardDescription>
          <div class="flex items-center gap-4 text-sm text-muted-foreground">
            <span class="flex items-center gap-1">
              <svg class="w-5 h-5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ schedule.duration }} {{ t('common.min') }}
            </span>
            <span class="flex items-center gap-1">
              <svg class="w-5 h-5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" />
              </svg>
              {{ schedule.timezone }}
            </span>
          </div>
          <Button
            class="w-full mt-4 gap-2"
            variant="outline"
            :disabled="navigatingId === schedule.id"
            @click.stop="selectSchedule(schedule.id)"
          >
            <svg
              v-if="navigatingId === schedule.id"
              class="w-4 h-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ t('public.profile.selectTime') }}
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>

  <div v-else class="text-center py-12 text-muted-foreground">
    <p class="text-lg font-medium">{{ t('public.profile.notFound') }}</p>
  </div>
  </div>
</template>
