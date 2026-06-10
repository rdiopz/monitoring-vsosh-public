import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import router from '@/app/router'

import { authAPI } from '@services/api'

export const useAuthStore = defineStore('auth', () => {
  const toast = useToast()

  // Состояние
  const user = ref(null)
  const isLoading = ref(false)
  const isInitialized = ref(false)
  const accessToken = ref(null)

  // Геттеры
  const isAuthenticated = computed(() => !!user.value)
  const userEmail = computed(() => user.value?.email || '')
  const userRole = computed(() => user.value?.role_name || '')
  const userId = computed(() => user.value?.user_id || null)
  const userCreatedAt = computed(() => user.value?.created_at || null)
  const userPasswordChangedAt = computed(() => user.value?.password_changed_at || null)

  // Очистить данные пользователя
  const clearUser = () => {
    user.value = null
  }

  // Очистить токен
  const clearAccessToken = () => {
    accessToken.value = null
  }

  // Установить токен
  const setAccessToken = (token) => {
    accessToken.value = token
  }

  // Преобразует формат ответа
  const toUser = (data) => ({
    user_id: data.user_id,
    email: data.email,
    role_name: data.role_name ?? data.role,
    created_at: data.created_at,
    password_changed_at: data.password_changed_at,
  })

  // Убрать всю информацию
  const resetAuth = () => {
    clearUser()
    clearAccessToken()
  }

  // Инициализация при загрузке
  const initializeAuth = async () => {
    if (isInitialized.value) return
    isInitialized.value = true

    if (!document.cookie.includes('has_refresh_token=true')) {
      resetAuth()
      return
    }

    try {
      const { data } = await authAPI.getProfile()
      user.value = toUser(data)
    } catch {
      resetAuth()
    }
  }

  // Вход в систему
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const { data } = await authAPI.login(credentials)
      const { access, message } = data

      setAccessToken(access)
      user.value = toUser(data)
      toast.success(message)

      return { access, user_id: data.user_id, email: data.email, role: data.role }
    } catch {
      clearUser()
    } finally {
      isLoading.value = false
    }
  }

  // Выход из системы
  const logout = async () => {
    try {
      const response = await authAPI.logout()
      toast.success(response.data.message)
    } catch (error) {
      console.warn('Выход не удался:', error)
    } finally {
      resetAuth()
      router.push({ name: 'Login' })
    }
  }

  // Загрузка профиля
  const fetchProfile = async () => {
    isLoading.value = true
    try {
      const response = await authAPI.getProfile()
      user.value = toUser(response.data)
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  // Обновление профиля
  const updateProfile = async (data) => {
    isLoading.value = true
    try {
      const response = await authAPI.updateProfile(data)
      user.value = toUser(response.data)
      toast.success('Успешное измение данных профиля')
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  // Частичное обновление профиля
  const updateProfilePartial = async (data) => {
    isLoading.value = true
    try {
      const response = await authAPI.updateProfilePartial(data)
      user.value = toUser(response.data)
      toast.success('Успешное измение данных профиля')
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  // Смена пароля
  const changePassword = async (data) => {
    isLoading.value = true
    try {
      const response = await authAPI.changePassword(data)
      const { message } = response.data
      toast.success(message)
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  // Обновить токен (через refresh cookie)
  const refreshToken = async () => {
    const response = await authAPI.refreshToken()
    const { access } = response.data
    setAccessToken(access)
    return access
  }

  return {
    user,
    isLoading,
    isInitialized,
    accessToken,

    isAuthenticated,
    userEmail,
    userRole,
    userId,
    userCreatedAt,
    userPasswordChangedAt,

    initializeAuth,
    clearUser,
    setAccessToken,
    clearAccessToken,
    login,
    logout,
    fetchProfile,
    updateProfile,
    updateProfilePartial,
    changePassword,
    refreshToken,
  }
})
