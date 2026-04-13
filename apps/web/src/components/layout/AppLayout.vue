<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/button/Button.vue'

const route = useRoute()
const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Top nav -->
    <header class="border-b border-border bg-background">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 rounded-md bg-primary flex items-center justify-center">
            <span class="text-primary-foreground text-sm font-bold">S</span>
          </div>
          <span class="font-semibold text-lg text-foreground">SlotBook</span>
        </div>

        <!-- Nav tabs -->
        <nav class="flex items-center gap-1">
          <RouterLink
            to="/dashboard"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-md text-base font-medium transition-colors',
              route.path === '/dashboard'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            События
          </RouterLink>
          <RouterLink
            to="/bookings"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-md text-base font-medium transition-colors',
              route.path === '/bookings'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50',
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            Бронирования
          </RouterLink>
        </nav>

        <!-- User menu -->
        <Button variant="ghost" @click="authStore.logout">
          Выйти
        </Button>
      </div>
    </header>

    <!-- Page content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>
  </div>
</template>
