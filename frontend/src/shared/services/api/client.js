import axios from 'axios'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@entities/auth'
import router from '@/app/router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const toast = useToast()

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// Добавляем токен к запросу
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken && !config.url?.includes('/auth/refresh/')) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

// Флаг и очередь для refresh токена
let isRefreshing = false
let failedQueue = []
const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve(token)
  })
  failedQueue = []
}

// Ответы сервера
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const isRefreshRequest = originalRequest.url?.includes('/auth/refresh/')

    // 401 — пытаемся обновить токен
    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshRequest) {
      // Проверяем, есть ли refresh token в cookie
      const hasRefreshToken = document.cookie.includes('has_refresh_token=true')
      if (!hasRefreshToken) {
        // Рефрешить нечем — сразу на логин, без лишнего запроса
        const authStore = useAuthStore()
        authStore.clearUser()
        authStore.clearAccessToken()
        router.replace({ name: 'Login' })
        toast.error('Сессия истекла. Выполните вход заново.')
        return Promise.reject(error)
      }

      originalRequest._retry = true

      // Если уже обновляем — ждём в очереди
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      isRefreshing = true
      try {
        // Запрос на обновление токена
        const authStore = useAuthStore()
        const newToken = await authStore.refreshToken()

        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`

        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)

        const message = 'Сессия истекла. Выполните вход заново.'
        toast.error(message)

        const authStore = useAuthStore()
        authStore.clearUser()
        authStore.clearAccessToken()
        router.replace({ name: 'Login' })

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Показываем другие ошибки
    if (error.response?.status !== 401) {
      handleError(error)
    }

    return Promise.reject(error)
  },
)

// Обработка ошибок
const handleError = (error) => {
  if (!error.response) {
    toast.error('Не удается подключиться к серверу.')
    return
  }

  const { status, data } = error.response

  const messages = {
    400: () => {
      if (data.detail) {
        return Array.isArray(data.detail) ? data.detail[0] : data.detail
      }
      if (data.message) return data.message

      // Показываем только сообщение, без имени поля
      const [fieldName, errors] = Object.entries(data)[0] || []
      if (fieldName && errors) {
        const message = Array.isArray(errors) ? errors[0] : errors
        return message
      }
      return 'Ошибка валидации.'
    },
    403: () => 'У вас нет прав для выполнения этого действия.',
    404: () => 'Запрашиваемый ресурс не найден.',
    422: () => {
      if (data.detail) return data.detail
      return 'Ошибка валидации.'
    },
    429: () => 'Слишком много запросов. Попробуйте позже.',
    500: () => 'Ошибка сервера. Попробуйте позже.',
    503: () => 'Сервер временно недоступен. Попробуйте позже.',
  }

  toast.error(messages[status]?.() || 'Произошла неожиданная ошибка.')
}

export default api
