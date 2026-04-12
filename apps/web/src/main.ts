import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'

const i18n = createI18n({
  legacy: false,
  locale: 'ru',
  fallbackLocale: 'en',
  messages: {
    ru: {},
    en: {},
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueQueryPlugin)
app.use(i18n)

app.mount('#app')
