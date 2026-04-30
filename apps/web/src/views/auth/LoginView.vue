<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuthStore } from '@/stores/auth'
import Card from '@/components/ui/card/Card.vue'
import CardHeader from '@/components/ui/card/CardHeader.vue'
import CardTitle from '@/components/ui/card/CardTitle.vue'
import CardDescription from '@/components/ui/card/CardDescription.vue'
import CardContent from '@/components/ui/card/CardContent.vue'
import CardFooter from '@/components/ui/card/CardFooter.vue'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import { RouterLink } from 'vue-router'
import { BASE_URL } from '@/api/client'

const { t } = useI18n()

const schema = computed(() =>
  toTypedSchema(
    z.object({
      email: z.string().email(t('auth.validation.invalidEmail')),
      password: z.string().min(6, t('auth.validation.minChars6')),
    }),
  ),
)

const { handleSubmit, defineField, errors } = useForm({ validationSchema: schema })
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const authStore = useAuthStore()
const serverError = ref<string | null>(null)
const demoLoading = ref(false)

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authStore.login(values)
  } catch {
    serverError.value = t('auth.login.invalidCredentials')
  }
})

async function loginAsDemo() {
  demoLoading.value = true
  try {
    await authStore.login({ email: 'john@example.com', password: 'changeme' })
  } finally {
    demoLoading.value = false
  }
}
</script>

<template>
  <div class="center-page flex items-center justify-center px-4">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle>{{ t('auth.login.title') }}</CardTitle>
        <CardDescription>{{ t('auth.login.description') }}</CardDescription>
      </CardHeader>

      <form @submit.prevent="onSubmit">
        <CardContent class="space-y-4">
          <div class="space-y-1.5">
            <Label for="email">{{ t('common.email') }}</Label>
            <Input
              id="email"
              v-model="email"
              v-bind="emailAttrs"
              type="email"
              placeholder="you@example.com"
            />
            <p v-if="errors.email" class="text-base text-destructive">{{ errors.email }}</p>
          </div>

          <div class="space-y-1.5">
            <Label for="password">{{ t('auth.login.password') }}</Label>
            <Input
              id="password"
              v-model="password"
              v-bind="passwordAttrs"
              type="password"
              placeholder="••••••••"
            />
            <p v-if="errors.password" class="text-base text-destructive">{{ errors.password }}</p>
          </div>

          <p v-if="serverError" class="text-base text-destructive">{{ serverError }}</p>
        </CardContent>

        <CardFooter class="flex flex-col gap-3">
          <Button type="submit" class="w-full gap-2" :disabled="authStore.isLoading">
            <svg
              v-if="authStore.isLoading"
              class="w-4 h-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ authStore.isLoading ? t('auth.login.submitting') : t('auth.login.submitBtn') }}
          </Button>

          <p class="text-base text-muted-foreground text-center">
            {{ t('auth.login.noAccount') }}
            <RouterLink to="/register" class="text-primary underline-offset-4 hover:underline">
              {{ t('auth.login.register') }}
            </RouterLink>
          </p>
        </CardFooter>
      </form>

      <div class="px-6 pb-6 flex flex-col gap-3">
        <div class="relative w-full flex items-center gap-2">
          <div class="flex-1 border-t border-border" />
          <span class="text-xs text-muted-foreground">{{ t('auth.login.or') }}</span>
          <div class="flex-1 border-t border-border" />
        </div>

        <a
          :href="`${BASE_URL}/auth/google`"
          class="w-full rounded-md border border-border px-4 py-2 text-sm text-foreground hover:bg-accent transition-colors flex items-center justify-center gap-2"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          {{ t('auth.login.google') }}
        </a>

        <button
          class="w-full rounded-md border border-dashed border-border px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
          :disabled="demoLoading"
          @click="loginAsDemo"
        >
          <svg
            v-if="demoLoading"
            class="w-4 h-4 animate-spin"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {{ t('auth.login.demo') }}
        </button>

        <RouterLink
          to="/"
          class="w-full rounded-md px-4 py-2 text-sm text-center text-muted-foreground hover:text-foreground transition-colors"
        >
          {{ t('auth.login.asGuest') }}
        </RouterLink>
      </div>
    </Card>
  </div>
</template>

<style scoped>
.center-page {
  min-height: calc(100dvh - 5rem - env(safe-area-inset-top));
}
@media (min-width: 640px) {
  .center-page {
    min-height: calc(100dvh - 4rem - env(safe-area-inset-top));
  }
}
</style>
