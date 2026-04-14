<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Button from '@/components/ui/button/Button.vue'

const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

onMounted(() => {
  if (!authStore.user) authStore.fetchMe()
})
</script>

<template>
  <div class="min-h-screen bg-background min-w-[375px]">
    <!-- Top nav -->
    <header class="border-b border-border bg-background sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2 select-none">
          <div class="w-9 h-9 rounded-md bg-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-foreground" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <span class="font-semibold text-lg text-foreground hidden sm:block">SlotBook</span>
        </RouterLink>

        <!-- Nav tabs -->
        <nav class="flex items-center gap-1">
          <RouterLink
            to="/dashboard"
            :class="[
              'inline-flex items-center gap-2 p-3 sm:px-4 sm:py-2 rounded-md text-base font-medium transition-colors min-h-[44px]',
              route.path === '/dashboard'
                ? 'bg-secondary text-primary'
                : 'text-muted-foreground hover:text-primary hover:bg-accent',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="hidden sm:inline">События</span>
          </RouterLink>
          <RouterLink
            to="/bookings"
            :class="[
              'inline-flex items-center gap-2 p-3 sm:px-4 sm:py-2 rounded-md text-base font-medium transition-colors min-h-[44px]',
              route.path === '/bookings'
                ? 'bg-secondary text-primary'
                : 'text-muted-foreground hover:text-primary hover:bg-accent',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            <span class="hidden sm:inline">Бронирования</span>
          </RouterLink>
        </nav>

        <!-- User menu -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium select-none">
              {{ authStore.user?.name?.charAt(0).toUpperCase() ?? '?' }}
            </div>
            <span class="text-sm font-medium text-foreground hidden sm:block">{{ authStore.user?.name }}</span>
          </div>
          <Button variant="ghost" size="icon" class="w-9 h-9 text-muted-foreground" title="Выйти" @click="authStore.logout">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </Button>
        </div>
      </div>
    </header>

    <!-- Page content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>
  </div>

  <!-- Global toast -->
  <Transition name="toast">
    <div
      v-if="toast.message.value"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-muted/90 backdrop-blur-sm text-muted-foreground text-sm rounded-lg px-5 py-3 shadow-md min-w-64 max-w-sm"
    >
      <p class="font-medium">{{ toast.message.value }}</p>
      <p v-if="toast.detail.value" class="text-xs opacity-70 mt-1 break-all">{{ toast.detail.value }}</p>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}
</style>
