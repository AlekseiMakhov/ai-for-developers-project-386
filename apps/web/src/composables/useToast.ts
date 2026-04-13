import { ref } from 'vue'

const message = ref<string | null>(null)
const detail = ref<string | null>(null)
let timer: ReturnType<typeof setTimeout> | null = null

export function useToast() {
  function show(msg: string, det?: string, duration = 3000) {
    message.value = msg
    detail.value = det ?? null
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      message.value = null
      detail.value = null
    }, duration)
  }

  function hide() {
    message.value = null
    detail.value = null
    if (timer) clearTimeout(timer)
  }

  return { message, detail, show, hide }
}
