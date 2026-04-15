import { defineConfig, minimalPreset } from '@vite-pwa/assets-generator/config'

export default defineConfig({
  preset: {
    ...minimalPreset,
    apple: {
      sizes: [180],
      padding: 0.1,
    },
    maskable: {
      sizes: [512],
      padding: 0.05,
    },
    transparent: {
      sizes: [64, 192, 512],
      padding: 0,
      favicons: [[64, 'favicon.ico']],
    },
  },
  images: ['public/favicon.svg'],
})
