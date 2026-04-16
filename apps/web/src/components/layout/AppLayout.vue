<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Button from '@/components/ui/button/Button.vue'
import LanguageSwitcher from '@/components/layout/LanguageSwitcher.vue'
import Tooltip from '@/components/ui/tooltip/Tooltip.vue'

const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()
const { t } = useI18n()

onMounted(() => {
  if (!authStore.user) authStore.fetchMe()
})
</script>

<template>
  <div class="h-dvh flex flex-col bg-background">
    <!-- Top nav -->
    <header class="shrink-0 border-b border-border bg-background sticky top-0 z-10 pt-[env(safe-area-inset-top)]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 sm:h-16 flex items-center justify-between gap-3">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-3 sm:gap-2 select-none shrink-0">
          <div class="w-12 h-12 sm:w-9 sm:h-9 rounded-xl sm:rounded-md bg-primary flex items-center justify-center">
            <svg class="w-7 h-7 sm:w-5 sm:h-5 text-primary-foreground" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <span class="font-semibold text-xl sm:text-lg text-foreground">Slotbook</span>
        </RouterLink>

        <!-- Desktop nav tabs (hidden on mobile — shown in bottom bar instead) -->
        <nav class="hidden sm:flex items-center gap-1">
          <RouterLink
            to="/dashboard"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-md text-base font-medium transition-colors',
              route.path === '/dashboard'
                ? 'bg-secondary text-primary'
                : 'text-muted-foreground hover:text-primary hover:bg-accent',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ t('nav.events') }}
          </RouterLink>
          <RouterLink
            to="/bookings"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-md text-base font-medium transition-colors',
              route.path === '/bookings'
                ? 'bg-secondary text-primary'
                : 'text-muted-foreground hover:text-primary hover:bg-accent',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            {{ t('nav.bookings') }}
          </RouterLink>
        </nav>

        <!-- User menu -->
        <div class="flex items-center gap-2 ml-auto sm:ml-0">
          <LanguageSwitcher />
          <div class="flex items-center gap-2">
            <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium select-none shrink-0">
              {{ authStore.user?.name?.charAt(0).toUpperCase() ?? '?' }}
            </div>
            <span class="text-sm font-medium text-foreground hidden sm:block">{{ authStore.user?.name }}</span>
          </div>
          <Tooltip :text="t('nav.logout')">
            <Button variant="ghost" size="icon" class="w-11 h-11 sm:w-9 sm:h-9 text-muted-foreground" @click="authStore.logout">
              <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </Button>
          </Tooltip>
        </div>
      </div>
    </header>

    <!-- Page content -->
    <main class="flex-1 min-h-0 overflow-y-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-full flex flex-col">
        <RouterView />
      </div>
    </main>

    <!-- Mobile bottom tab bar (in-flow, not fixed) -->
    <nav class="sm:hidden shrink-0 border-t border-border bg-background safe-area-bottom">
      <div class="flex justify-center gap-12 h-20 items-center">
        <RouterLink
          to="/dashboard"
          :class="[
            'flex flex-col items-center gap-2 transition-colors w-16',
            route.path === '/dashboard' ? 'text-primary' : 'text-muted-foreground',
          ]"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="text-sm font-medium">{{ t('nav.events') }}</span>
        </RouterLink>
        <RouterLink
          to="/bookings"
          :class="[
            'flex flex-col items-center gap-2 transition-colors w-16',
            route.path === '/bookings' ? 'text-primary' : 'text-muted-foreground',
          ]"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          <span class="text-sm font-medium">{{ t('nav.bookings') }}</span>
        </RouterLink>
      </div>
    </nav>
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

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
