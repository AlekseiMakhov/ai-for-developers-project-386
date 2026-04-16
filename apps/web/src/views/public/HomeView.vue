<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import Button from '@/components/ui/button/Button.vue'

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col items-center text-center py-16 gap-10">
    <!-- Hero -->
    <div class="flex flex-col items-center gap-4 max-w-xl">
      <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center shadow-md">
        <svg class="w-9 h-9 text-primary-foreground" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
      </div>
      <h1 class="text-4xl font-bold tracking-tight text-foreground">Slotbook</h1>
      <p class="text-lg text-muted-foreground leading-relaxed">
        {{ t('public.home.tagline') }}
      </p>
    </div>

    <!-- CTA -->
    <div class="flex flex-col sm:flex-row gap-3">
      <Button as-child size="lg" class="text-base px-8">
        <RouterLink to="/hosts">{{ t('public.home.bookBtn') }}</RouterLink>
      </Button>
      <Button as-child size="lg" variant="outline" class="text-base px-8">
        <RouterLink to="/login">{{ t('public.home.loginBtn') }}</RouterLink>
      </Button>
    </div>

    <!-- Features -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6 w-full max-w-3xl text-left">
      <div class="rounded-xl border border-border p-5 flex flex-col gap-2">
        <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </div>
        <h3 class="font-semibold text-foreground">{{ t('public.home.feature1Title') }}</h3>
        <p class="text-sm text-muted-foreground">{{ t('public.home.feature1Desc') }}</p>
      </div>
      <div class="rounded-xl border border-border p-5 flex flex-col gap-2">
        <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <circle cx="10" cy="7" r="4" />
            <path d="M4 21v-2a4 4 0 0 1 4-4h4" />
            <line x1="19" y1="11" x2="19" y2="17" />
            <line x1="16" y1="14" x2="22" y2="14" />
          </svg>
        </div>
        <h3 class="font-semibold text-foreground">{{ t('public.home.feature2Title') }}</h3>
        <p class="text-sm text-muted-foreground">{{ t('public.home.feature2Desc') }}</p>
      </div>
      <div class="rounded-xl border border-border p-5 flex flex-col gap-2">
        <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <polyline points="9 11 12 14 22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
        </div>
        <h3 class="font-semibold text-foreground">{{ t('public.home.feature3Title') }}</h3>
        <p class="text-sm text-muted-foreground">{{ t('public.home.feature3Desc') }}</p>
      </div>
    </div>
  </div>
</template>
