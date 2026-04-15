<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Platform detection
const ua = navigator.userAgent
const isIos = /iphone|ipad|ipod/i.test(ua)
const isIosSafari =
  isIos && /safari/i.test(ua) && !/crios|fxios|opios|edgios/i.test(ua)
const isStandalone =
  ('standalone' in navigator && (navigator as { standalone?: boolean }).standalone === true) ||
  window.matchMedia('(display-mode: standalone)').matches

type Mode = 'android' | 'ios-safari' | 'ios-other' | null

const mode = ref<Mode>(null)
const visible = ref(false)
const dismissed = ref(false)

// BeforeInstallPromptEvent is non-standard, define locally
interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

let deferredPrompt: BeforeInstallPromptEvent | null = null

function dismiss() {
  visible.value = false
  dismissed.value = true
  sessionStorage.setItem('pwa-prompt-dismissed', '1')
}

async function installAndroid() {
  if (!deferredPrompt) return
  await deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice
  if (outcome === 'accepted') {
    visible.value = false
  }
  deferredPrompt = null
}

function handleInstallPrompt(e: Event) {
  e.preventDefault()
  deferredPrompt = e as BeforeInstallPromptEvent
  if (!dismissed.value) {
    mode.value = 'android'
    visible.value = true
  }
}

onMounted(() => {
  // Already installed — don't show
  if (isStandalone) return
  // Already dismissed this session
  if (sessionStorage.getItem('pwa-prompt-dismissed')) return

  if (isIosSafari) {
    mode.value = 'ios-safari'
    visible.value = true
  } else if (isIos) {
    mode.value = 'ios-other'
    visible.value = true
  } else {
    window.addEventListener('beforeinstallprompt', handleInstallPrompt)
  }
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', handleInstallPrompt)
})
</script>

<template>
  <Transition
    enter-active-class="transition-transform duration-300 ease-out"
    enter-from-class="translate-y-full"
    enter-to-class="translate-y-0"
    leave-active-class="transition-transform duration-200 ease-in"
    leave-from-class="translate-y-0"
    leave-to-class="translate-y-full"
  >
    <div
      v-if="visible"
      class="fixed bottom-0 inset-x-0 z-50 pb-[env(safe-area-inset-bottom)]"
    >
      <div class="mx-4 mb-4 rounded-2xl bg-white shadow-xl border border-gray-100 p-4">
        <!-- Android / Desktop: native install -->
        <template v-if="mode === 'android'">
          <div class="flex items-center gap-3">
            <img src="/pwa-64x64.png" alt="Slotbook" class="w-12 h-12 rounded-xl flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm">Установить Slotbook</p>
              <p class="text-xs text-gray-500 mt-0.5">Работает без интернета</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button
                class="text-xs text-gray-400 px-3 py-1.5 rounded-lg hover:bg-gray-50"
                @click="dismiss"
              >
                Позже
              </button>
              <button
                class="text-xs font-medium text-white bg-blue-600 px-3 py-1.5 rounded-lg hover:bg-blue-700"
                @click="installAndroid"
              >
                Установить
              </button>
            </div>
          </div>
        </template>

        <!-- iOS Safari: manual instruction -->
        <template v-else-if="mode === 'ios-safari'">
          <div class="flex items-start gap-3">
            <img src="/pwa-64x64.png" alt="Slotbook" class="w-12 h-12 rounded-xl flex-shrink-0 mt-0.5" />
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm">Добавить на экран «Домой»</p>
              <p class="text-xs text-gray-500 mt-1 leading-relaxed">
                Нажмите
                <span class="inline-flex items-center gap-0.5 font-medium text-gray-700">
                  <!-- Share icon -->
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  Поделиться
                </span>
                → «На экран «Домой»»
              </p>
            </div>
            <button class="text-gray-300 hover:text-gray-400 flex-shrink-0" @click="dismiss">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </template>

        <!-- iOS other browser: suggest Safari -->
        <template v-else-if="mode === 'ios-other'">
          <div class="flex items-start gap-3">
            <img src="/pwa-64x64.png" alt="Slotbook" class="w-12 h-12 rounded-xl flex-shrink-0 mt-0.5" />
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm">Установить приложение</p>
              <p class="text-xs text-gray-500 mt-1 leading-relaxed">
                Откройте эту страницу в Safari, чтобы добавить приложение на экран «Домой»
              </p>
            </div>
            <button class="text-gray-300 hover:text-gray-400 flex-shrink-0" @click="dismiss">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </template>
      </div>
    </div>
  </Transition>
</template>
