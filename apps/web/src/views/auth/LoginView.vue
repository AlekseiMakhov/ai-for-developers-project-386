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

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authStore.login(values)
  } catch {
    serverError.value = t('auth.login.invalidCredentials')
  }
})
</script>

<template>
  <div class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4">
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
          <Button type="submit" class="w-full" :disabled="authStore.isLoading">
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

        <button
          class="w-full rounded-md border border-dashed border-border px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors"
          @click="authStore.login({ email: 'john@example.com', password: 'changeme' })"
        >
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
