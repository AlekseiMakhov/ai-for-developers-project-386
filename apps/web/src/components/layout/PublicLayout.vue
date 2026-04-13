<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Minimal top bar -->
    <header class="border-b border-border bg-background">
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
            <span class="text-primary-foreground text-xs font-bold">S</span>
          </div>
          <span class="font-semibold text-base text-foreground">SlotBook</span>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
