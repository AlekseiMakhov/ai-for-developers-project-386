<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import { getHosts } from '@/api/bookings'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Card from '@/components/ui/card/Card.vue'
import CardHeader from '@/components/ui/card/CardHeader.vue'
import CardTitle from '@/components/ui/card/CardTitle.vue'
import CardDescription from '@/components/ui/card/CardDescription.vue'
import CardContent from '@/components/ui/card/CardContent.vue'
import CardFooter from '@/components/ui/card/CardFooter.vue'

const PAGE_SIZE = 12

const searchInput = ref('')
const search = ref('')
const page = ref(1)

let debounceTimer: ReturnType<typeof setTimeout> | null = null
watch(searchInput, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    search.value = val
    page.value = 1
  }, 350)
})

const { data, isLoading, isError } = useQuery({
  queryKey: ['hosts', search, page],
  queryFn: () => getHosts({ search: search.value || undefined, page: page.value, pageSize: PAGE_SIZE }),
})

const totalPages = computed(() => {
  if (!data.value) return 1
  return Math.ceil(data.value.total / PAGE_SIZE)
})

</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl font-bold text-foreground">Специалисты</h1>
      <p class="text-muted-foreground">Выберите специалиста и забронируйте удобное время</p>
    </div>

    <!-- Search -->
    <div class="max-w-sm">
      <Input
        v-model="searchInput"
        placeholder="Поиск по имени..."
        class="w-full"
      />
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="i in PAGE_SIZE"
        :key="i"
        class="rounded-xl border border-border p-5 flex flex-col gap-3 animate-pulse"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-muted" />
          <div class="flex flex-col gap-1.5 flex-1">
            <div class="h-4 bg-muted rounded w-2/3" />
            <div class="h-3 bg-muted rounded w-1/2" />
          </div>
        </div>
        <div class="h-8 bg-muted rounded mt-1" />
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="isError" class="text-center py-16 text-destructive">
      Не удалось загрузить список специалистов. Попробуйте позже.
    </div>

    <!-- Empty -->
    <div
      v-else-if="data && data.items.length === 0"
      class="text-center py-16 flex flex-col items-center gap-3"
    >
      <svg class="w-12 h-12 text-muted-foreground/40" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
      <p class="text-muted-foreground text-lg">Специалисты не найдены</p>
      <p v-if="search" class="text-sm text-muted-foreground">
        Попробуйте изменить поисковый запрос
      </p>
    </div>

    <!-- Grid -->
    <div v-else-if="data" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card v-for="host in data.items" :key="host.id" class="flex flex-col">
        <CardHeader class="pb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <span class="text-primary font-semibold text-base uppercase">
                {{ host.name.charAt(0) }}
              </span>
            </div>
            <div class="min-w-0">
              <CardTitle class="text-base truncate">{{ host.name }}</CardTitle>
              <CardDescription class="text-xs truncate">{{ host.timezone }}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent class="pb-3 flex-1">
          <p class="text-sm text-muted-foreground">
            {{ host.scheduleCount }}
            {{ host.scheduleCount === 1 ? 'расписание' : host.scheduleCount < 5 ? 'расписания' : 'расписаний' }}
          </p>
        </CardContent>
        <CardFooter>
          <Button as-child class="w-full" size="sm">
            <RouterLink :to="`/book/${host.slug}`">Записаться</RouterLink>
          </Button>
        </CardFooter>
      </Card>
    </div>

    <!-- Pagination -->
    <div v-if="data && totalPages > 1" class="flex items-center justify-center gap-2 pt-2">
      <Button
        variant="outline"
        size="sm"
        :disabled="page <= 1"
        @click="page--"
      >
        ← Назад
      </Button>
      <span class="text-sm text-muted-foreground px-2">
        {{ page }} / {{ totalPages }}
      </span>
      <Button
        variant="outline"
        size="sm"
        :disabled="page >= totalPages"
        @click="page++"
      >
        Вперёд →
      </Button>
    </div>
  </div>
</template>
