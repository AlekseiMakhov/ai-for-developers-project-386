<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'
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
      name: z.string().min(2, t('auth.validation.minChars2')).max(30, t('auth.validation.maxChars30')),
      email: z.string().email(t('auth.validation.invalidEmail')),
      password: z.string().min(6, t('auth.validation.minChars6')),
      slug: z
        .string()
        .min(3, t('auth.validation.minChars3'))
        .regex(/^[a-z0-9-]+$/, t('auth.validation.slugFormat')),
      timezone: z.string().default('UTC'),
    }),
  ),
)

const { handleSubmit, defineField, errors } = useForm({ validationSchema: schema })
const [name, nameAttrs] = defineField('name')
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')
const [slug, slugAttrs] = defineField('slug')

const authStore = useAuthStore()
const serverError = ref<string | null>(null)
const emailExistsToast = ref(false)

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  emailExistsToast.value = false
  try {
    await authStore.register({ ...values, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone })
  } catch (e) {
    if (e instanceof ApiError && e.status === 409) {
      emailExistsToast.value = true
    } else {
      serverError.value = t('auth.register.serverError')
    }
  }
})
</script>

<template>
  <!-- Toast: email already exists -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="emailExistsToast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg max-w-sm w-[calc(100%-2rem)] text-sm"
      >
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M12 4a8 8 0 100 16A8 8 0 0012 4z" />
        </svg>
        <span class="flex-1">{{ t('auth.register.emailExists') }}</span>
        <button class="hover:opacity-75 shrink-0" @click="emailExistsToast = false">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Transition>
  </Teleport>

  <div class="center-page flex items-center justify-center px-4">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle>{{ t('auth.register.title') }}</CardTitle>
        <CardDescription>{{ t('auth.register.description') }}</CardDescription>
      </CardHeader>

      <form @submit.prevent="onSubmit">
        <CardContent class="space-y-4">
          <div class="space-y-1.5">
            <Label for="name">{{ t('auth.register.name') }}</Label>
            <Input id="name" v-model="name" v-bind="nameAttrs" :placeholder="t('auth.register.namePlaceholder')" maxlength="30" />
            <p v-if="errors.name" class="text-base text-destructive">{{ errors.name }}</p>
          </div>

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
            <Label for="password">{{ t('auth.register.password') }}</Label>
            <Input
              id="password"
              v-model="password"
              v-bind="passwordAttrs"
              type="password"
              placeholder="••••••••"
            />
            <p v-if="errors.password" class="text-base text-destructive">{{ errors.password }}</p>
          </div>

          <div class="space-y-1.5">
            <Label for="slug">{{ t('auth.register.slug') }}</Label>
            <div class="flex items-center gap-1">
              <span class="text-base text-muted-foreground whitespace-nowrap">slotbook.app/</span>
              <Input id="slug" v-model="slug" v-bind="slugAttrs" :placeholder="t('auth.register.slugPlaceholder')" />
            </div>
            <p v-if="errors.slug" class="text-base text-destructive">{{ errors.slug }}</p>
          </div>

          <p v-if="serverError" class="text-base text-destructive">{{ serverError }}</p>
        </CardContent>

        <CardFooter class="flex flex-col gap-3">
          <Button type="submit" class="w-full" :disabled="authStore.isLoading">
            {{ authStore.isLoading ? t('auth.register.submitting') : t('auth.register.submitBtn') }}
          </Button>
          <p class="text-base text-muted-foreground text-center">
            {{ t('auth.register.haveAccount') }}
            <RouterLink to="/login" class="text-primary underline-offset-4 hover:underline">
              {{ t('auth.register.loginLink') }}
            </RouterLink>
          </p>
        </CardFooter>
      </form>
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
