import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      // Основной
      '@': fileURLToPath(new URL('./src', import.meta.url)),

      // Слои FSD
      '@app': fileURLToPath(new URL('./src/app', import.meta.url)),
      '@pages': fileURLToPath(new URL('./src/pages', import.meta.url)),
      '@widgets': fileURLToPath(new URL('./src/widgets', import.meta.url)),
      '@features': fileURLToPath(new URL('./src/features', import.meta.url)),
      '@entities': fileURLToPath(new URL('./src/entities', import.meta.url)),
      '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),

      // App stores
      '@stores': fileURLToPath(new URL('./src/app/stores', import.meta.url)),

      // Shared UI
      '@ui': fileURLToPath(new URL('./src/shared/ui', import.meta.url)),
      '@icons': fileURLToPath(new URL('./src/shared/icons', import.meta.url)),

      // Shared lib
      '@lib': fileURLToPath(new URL('./src/shared/lib', import.meta.url)),
      '@utils': fileURLToPath(new URL('./src/shared/lib/utils', import.meta.url)),
      '@composables': fileURLToPath(new URL('./src/shared/lib/composables', import.meta.url)),

      // Shared services
      '@services': fileURLToPath(new URL('./src/shared/services', import.meta.url)),

      // Assets
      '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),

      // Features
      '@admin': fileURLToPath(new URL('./src/features/admin-panel', import.meta.url)),
      '@analysis': fileURLToPath(new URL('./src/features/analysis', import.meta.url)),
      '@auth': fileURLToPath(new URL('./src/features/auth', import.meta.url)),
      '@profile': fileURLToPath(new URL('./src/features/profile', import.meta.url)),
      '@operations': fileURLToPath(new URL('./src/features/data-operations', import.meta.url)),
    },
  },
  base: '/',
})
