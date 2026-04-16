<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { getToken } from '@/api/client'
import Button from '@/components/ui/button/Button.vue'
import LanguageSwitcher from '@/components/layout/LanguageSwitcher.vue'
import Tooltip from '@/components/ui/tooltip/Tooltip.vue'

const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

onMounted(() => {
  // Only attempt fetchMe when a token exists — authRequest redirects to /login
  // on 401, which would cause an infinite loop on the login page itself.
  if (!authStore.user && getToken()) authStore.fetchMe()
})
</script>

<template>
  <div class="h-dvh flex flex-col bg-background">
    <!-- Sticky top bar -->
    <header class="shrink-0 border-b border-border bg-background sticky top-0 z-10 pt-[env(safe-area-inset-top)]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 sm:h-16 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-3 sm:gap-2 select-none">
          <div class="w-12 h-12 sm:w-9 sm:h-9 rounded-xl sm:rounded-md bg-primary flex items-center justify-center">
            <svg class="w-7 h-7 sm:w-5 sm:h-5 text-primary-foreground" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <span class="font-semibold text-xl sm:text-base text-foreground">Slotbook</span>
        </RouterLink>

        <!-- Right side: language switcher + auth-aware button -->
        <div class="flex items-center gap-1">
          <LanguageSwitcher />
          <template v-if="authStore.user && route.name !== 'home'">
            <RouterLink to="/dashboard">
              <Tooltip :text="t('nav.dashboard')">
                <Button variant="ghost" size="icon" class="w-11 h-11 sm:w-9 sm:h-9 text-muted-foreground">
                  <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </Button>
              </Tooltip>
            </RouterLink>
          </template>
          <template v-else-if="route.name !== 'login' && route.name !== 'home'">
            <RouterLink to="/login">
              <Tooltip :text="t('nav.login')">
                <Button variant="ghost" size="icon" class="w-11 h-11 sm:w-9 sm:h-9 text-muted-foreground">
                  <svg class="w-6 h-6 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                </Button>
              </Tooltip>
            </RouterLink>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto">
      <div class="max-w-4xl mx-auto px-4">
        <RouterView />
      </div>
    </main>
  </div>
</template>
