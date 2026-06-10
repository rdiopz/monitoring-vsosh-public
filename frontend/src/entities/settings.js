import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { authAPI } from '@services/api'

export const useSettingsStore = defineStore('settings', () => {
  const toast = useToast()

  // Состояния
  const settings = ref([])
  const loading = ref(false)

  // Загрузить все настройки
  const fetchSettings = async () => {
    loading.value = true
    try {
      const response = await authAPI.getSettings()
      settings.value = response.data || []
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Загрузить период мониторинга
  const fetchMonitoringYears = async () => {
    loading.value = true
    try {
      const response = await authAPI.getMonitoringYears()
      const years = response.data.monitoring_years
      const setting = getSettingByKey('monitoring_years')
      if (setting) {
        setting.value = years
      } else {
        settings.value.push({ key: 'monitoring_years', value: years })
      }
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Обновить настройку
  const updateSetting = async (key, data) => {
    loading.value = true
    try {
      const response = await authAPI.updateSetting(key, data)
      const { message } = response.data
      toast.success(message)

      // Обновить локальное состояние
      const index = settings.value.findIndex((s) => s.key === key)
      if (index !== -1) {
        settings.value[index] = {
          ...settings.value[index],
          value: response.data.value,
        }
      }

      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Проверить код доступа
  const verifyCode = async (code) => {
    loading.value = true
    try {
      const response = await authAPI.verifyCode({ code })
      if (response.data.message) {
        toast.success(response.data.message)
      }
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Получить настройку по ключу
  const getSettingByKey = (key) => {
    return settings.value.find((s) => s.key === key)
  }

  // Получить значение настройки по ключу
  const getSettingValue = (key, defaultValue = null) => {
    const setting = getSettingByKey(key)
    return setting ? setting.value : defaultValue
  }

  // Сбросить состояние
  const resetState = () => {
    settings.value = []
  }

  return {
    settings,
    loading,

    fetchSettings,
    fetchMonitoringYears,
    updateSetting,
    verifyCode,
    getSettingByKey,
    getSettingValue,
    resetState,
  }
})
