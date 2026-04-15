import './assets/main.css'

import { createApp } from 'vue'
import { watch } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'
import ru from './locales/ru.json'
import en from './locales/en.json'

const STORAGE_KEY = 'lang'
const SUPPORTED = ['ru', 'en'] as const
type Lang = (typeof SUPPORTED)[number]

function detectLocale(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && SUPPORTED.includes(stored as Lang)) return stored as Lang
  return navigator.language.startsWith('ru') ? 'ru' : 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en',
  messages: { ru, en },
})

watch(i18n.global.locale, (val) => {
  localStorage.setItem(STORAGE_KEY, val)
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueQueryPlugin)
app.use(i18n)

app.mount('#app')
