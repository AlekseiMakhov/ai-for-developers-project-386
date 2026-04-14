<script setup lang="ts">
import {
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectItemIndicator,
} from 'radix-vue'

interface Option {
  value: string
  label: string
}

const props = defineProps<{
  modelValue?: string
  options: Option[]
  placeholder?: string
  id?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <SelectRoot
    :model-value="props.modelValue"
    :disabled="props.disabled"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <SelectTrigger
      :id="props.id"
      class="flex h-11 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-base focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
    >
      <SelectValue :placeholder="props.placeholder ?? ''" />
      <svg class="w-4 h-4 opacity-50 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
      </svg>
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        class="relative z-50 min-w-[var(--radix-select-trigger-width)] overflow-hidden rounded-md border border-border bg-popover text-popover-foreground shadow-md"
        :side-offset="4"
        position="popper"
      >
        <SelectViewport class="p-1">
          <SelectItem
            v-for="option in props.options"
            :key="option.value"
            :value="option.value"
            class="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-3 text-sm outline-none hover:bg-accent hover:text-primary data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[highlighted]:bg-accent data-[highlighted]:text-primary"
          >
            <SelectItemIndicator class="absolute left-2 flex h-4 w-4 items-center justify-center">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
              </svg>
            </SelectItemIndicator>
            <SelectItemText>{{ option.label }}</SelectItemText>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
