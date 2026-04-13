<script setup lang="ts">
import { ref } from 'vue'
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

const schema = toTypedSchema(
  z.object({
    name: z.string().min(2, 'Минимум 2 символа'),
    email: z.string().email('Введите корректный email'),
    password: z.string().min(6, 'Минимум 6 символов'),
    slug: z
      .string()
      .min(3, 'Минимум 3 символа')
      .regex(/^[a-z0-9-]+$/, 'Только строчные буквы, цифры и дефис'),
    timezone: z.string().default('UTC'),
  }),
)

const { handleSubmit, defineField, errors } = useForm({ validationSchema: schema })
const [name, nameAttrs] = defineField('name')
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')
const [slug, slugAttrs] = defineField('slug')

const authStore = useAuthStore()
const serverError = ref<string | null>(null)

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authStore.register({ ...values, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone })
  } catch {
    serverError.value = 'Ошибка регистрации. Проверьте данные и попробуйте снова.'
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle>Регистрация</CardTitle>
        <CardDescription>Создайте аккаунт SlotBook</CardDescription>
      </CardHeader>

      <form @submit.prevent="onSubmit">
        <CardContent class="space-y-4">
          <div class="space-y-1.5">
            <Label for="name">Имя</Label>
            <Input id="name" v-model="name" v-bind="nameAttrs" placeholder="Иван Иванов" />
            <p v-if="errors.name" class="text-sm text-destructive">{{ errors.name }}</p>
          </div>

          <div class="space-y-1.5">
            <Label for="email">Email</Label>
            <Input
              id="email"
              v-model="email"
              v-bind="emailAttrs"
              type="email"
              placeholder="you@example.com"
            />
            <p v-if="errors.email" class="text-sm text-destructive">{{ errors.email }}</p>
          </div>

          <div class="space-y-1.5">
            <Label for="password">Пароль</Label>
            <Input
              id="password"
              v-model="password"
              v-bind="passwordAttrs"
              type="password"
              placeholder="••••••••"
            />
            <p v-if="errors.password" class="text-sm text-destructive">{{ errors.password }}</p>
          </div>

          <div class="space-y-1.5">
            <Label for="slug">Ваш URL (slug)</Label>
            <div class="flex items-center gap-1">
              <span class="text-sm text-muted-foreground whitespace-nowrap">slotbook.app/</span>
              <Input id="slug" v-model="slug" v-bind="slugAttrs" placeholder="ivan-ivanov" />
            </div>
            <p v-if="errors.slug" class="text-sm text-destructive">{{ errors.slug }}</p>
          </div>

          <p v-if="serverError" class="text-sm text-destructive">{{ serverError }}</p>
        </CardContent>

        <CardFooter class="flex flex-col gap-3">
          <Button type="submit" class="w-full" :disabled="authStore.isLoading">
            {{ authStore.isLoading ? 'Создание...' : 'Создать аккаунт' }}
          </Button>
          <p class="text-sm text-muted-foreground text-center">
            Уже есть аккаунт?
            <RouterLink to="/login" class="text-primary underline-offset-4 hover:underline">
              Войти
            </RouterLink>
          </p>
        </CardFooter>
      </form>
    </Card>
  </div>
</template>
