import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { authAPI } from '@services/api'
import { useUIState } from '@composables/useUIState'

export const useUsersStore = defineStore('users', () => {
  const toast = useToast()

  // Данные
  const users = ref([])
  const reviewers = ref([])
  const loading = ref(false)
  const total = ref(0)

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    activeTab: 'users',
    search: '',
    sortBy: 'email',
    sortOrder: 'asc',
    roleFilter: [],
    statusFilter: [],
    lastLoginFrom: null,
    lastLoginTo: null,
    createdFrom: null,
    createdTo: null,
    filtersExtended: false,
    visibleColumns: ['user_id', 'email', 'role_name', 'last_login', 'created_at', 'is_active'],
    page: 1,
    pageSize: 20,
  })

  // Загрузить список пользователей
  const fetchUsers = async (params = {}) => {
    loading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.roleFilter.length > 0) requestParams.role__in = ui.roleFilter.join(',')
      if (ui.statusFilter.length > 0) requestParams.is_active = ui.statusFilter.join(',')
      if (ui.lastLoginFrom) requestParams.last_login_after = ui.lastLoginFrom
      if (ui.lastLoginTo) requestParams.last_login_before = ui.lastLoginTo
      if (ui.createdFrom) requestParams.created_after = ui.createdFrom
      if (ui.createdTo) requestParams.created_before = ui.createdTo

      const response = await authAPI.getUsers(requestParams)
      users.value = response.data.results || response.data
      total.value = response.data.count || users.value.length
      return response.data
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Загрузить пользователя по ID
  const fetchUser = async (id) => {
    loading.value = true
    try {
      const response = await authAPI.getUser(id)
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Загрузить список рассматривающих заявки
  const fetchReviewers = async () => {
    loading.value = true
    try {
      const response = await authAPI.getReviewers()
      reviewers.value = response.data || []
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Обновить пользователя (полное)
  const updateUser = async (id, data) => {
    loading.value = true
    try {
      const response = await authAPI.updateUser(id, data)
      toast.success('Успешное изменение данных пользователя')
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Обновить пользователя (частичное)
  const updateUserPartial = async (id, data) => {
    loading.value = true
    try {
      const response = await authAPI.updateUserPartial(id, data)
      toast.success('Успешное изменение данных пользователя')
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Сбросить состояние
  const resetState = () => {
    users.value = []
    reviewers.value = []
    total.value = 0
  }

  return {
    users,
    reviewers,
    loading,
    total,
    ui,
    getUIState,
    setUIState,

    fetchUsers,
    fetchUser,
    fetchReviewers,
    updateUser,
    updateUserPartial,
    resetState,
  }
})
