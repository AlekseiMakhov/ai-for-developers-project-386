<script setup lang="ts">
defineProps<{ text: string }>()
</script>

<template>
  <div class="relative inline-flex group">
    <slot />
    <span
      class="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-2 py-1 rounded text-xs font-medium whitespace-nowrap pointer-events-none z-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150 bg-white/95 text-foreground shadow-sm border border-border"
    >
      {{ text }}
    </span>
  </div>
</template>
