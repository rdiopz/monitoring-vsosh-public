import { defineStore } from 'pinia'
import { watch, computed } from 'vue'
import { useLocalStorage } from '@composables/useLocalStorage'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = useLocalStorage('theme', 'light', {
    serializer: (value) => value,
    deserializer: (value) => (value === 'dark' ? 'dark' : 'light'),
  })

  const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme)
  }

  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
  }

  const isDark = computed(() => currentTheme.value === 'dark')

  // Сразу применяем тему при инициализации
  applyTheme(currentTheme.value)

  // Обновляем DOM при смене темы
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    currentTheme,
    toggleTheme,
    isDark,
  }
})
