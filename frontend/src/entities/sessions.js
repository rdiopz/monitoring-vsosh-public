import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { authAPI } from '@services/api'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useSessionsStore = defineStore('sessions', () => {
  const toast = useToast()

  // Данные
  const sessions = ref([])
  const loading = ref(false)
  const total = ref(0)

  // Опции для фильтров (собираются динамически)
  const browserOptions = ref([])
  const platformOptions = ref([])

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    search: '',
    suspiciousFilter: null,
    deviceFilter: [],
    browserFilter: [],
    platformFilter: [],
    suspiciousFirst: true,
    visibleColumns: [
      'user_email',
      'device',
      'browser',
      'platform',
      'ip',
      'fingerprint',
      'created_at',
      'last_activity',
      'is_suspicious',
    ],
    page: 1,
    pageSize: 20,
  })
  // Загрузить сессии текущего пользователя
  const fetchSessions = async () => {
    loading.value = true
    try {
      const response = await authAPI.getSessions()
      sessions.value = response.data.results || []
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Загрузить все сессии (админ)
  const fetchAllSessions = async (params = {}) => {
    loading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        suspicious_first: ui.suspiciousFirst,
        ...params,
      }

      if (ui.suspiciousFilter !== null) requestParams.is_suspicious = ui.suspiciousFilter
      if (ui.deviceFilter.length > 0) requestParams.device__in = ui.deviceFilter.join(',')
      if (ui.browserFilter.length > 0) requestParams.browser__in = ui.browserFilter.join(',')
      if (ui.platformFilter.length > 0) requestParams.platform__in = ui.platformFilter.join(',')

      const response = await authAPI.getAllSessions(requestParams)
      sessions.value = response.data.results || []
      total.value = response.data.total || 0

      // Собираем уникальные браузеры и платформы для фильтров
      const browsers = new Set()
      const platforms = new Set()
      sessions.value.forEach((session) => {
        if (session.browser && session.browser !== 'Unknown') browsers.add(session.browser)
        if (session.platform && session.platform !== 'Unknown') platforms.add(session.platform)
      })
      browserOptions.value = Array.from(browsers).map((b) => ({ label: b, value: b }))
      platformOptions.value = Array.from(platforms).map((p) => ({ label: p, value: p }))

      return response.data
    } finally {
      loading.value = false
    }
  }

  // Завершить сессию по JTI (пользователь)
  const revokeSession = async (jti) => {
    loading.value = true
    try {
      const response = await authAPI.revokeSession(jti)
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Завершить сессию по JTI (админ)
  const adminDestroySession = async (jti) => {
    loading.value = true
    try {
      const response = await authAPI.adminDestroySession(jti)
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Выйти из всех сессий кроме текущей
  const logoutAll = async () => {
    loading.value = true
    try {
      const response = await authAPI.logoutAll()
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Завершить сессии по fingerprint (админ)
  const revokeByFingerprint = async (data) => {
    loading.value = true
    try {
      const response = await authAPI.revokeSessionByFingerprint(data)
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Завершить все сессии пользователя (админ)
  const revokeAllUserSessions = async (data) => {
    loading.value = true
    try {
      const response = await authAPI.revokeAllUserSessions(data)
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Сбросить состояние
  const resetState = () => {
    sessions.value = []
  }

  return {
    sessions,
    loading,
    total,
    browserOptions,
    platformOptions,
    ui,
    getUIState,
    setUIState,

    fetchSessions,
    fetchAllSessions,
    revokeSession,
    adminDestroySession,
    logoutAll,
    revokeByFingerprint,
    revokeAllUserSessions,
    resetState,
  }
})
