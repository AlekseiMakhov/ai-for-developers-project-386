<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Minimal top bar -->
    <header class="border-b border-border bg-background">
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center">
        <RouterLink to="/" class="flex items-center gap-2 select-none">
          <div class="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
            <svg class="w-4 h-4 text-primary-foreground" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <span class="font-semibold text-base text-foreground">SlotBook</span>
        </RouterLink>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
