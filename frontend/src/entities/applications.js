import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { authAPI } from '@services/api'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useApplicationsStore = defineStore('applications', () => {
  const toast = useToast()

  // Данные
  const applications = ref([])
  const currentApplication = ref(null)
  const loading = ref(false)
  const total = ref(0)

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    search: '',
    sortBy: 'application_datetime',
    sortOrder: 'desc',
    statusFilter: [],
    reviewedByFilter: [],
    dateFrom: null,
    dateTo: null,
    filtersExtended: false,
    visibleColumns: [
      'application_id',
      'email',
      'status',
      'application_datetime',
      'review_comment',
      'reviewed_by_email',
    ],
    page: 1,
    pageSize: 20,
  })

  // Загрузить список заявок
  const fetchApplications = async (params = {}) => {
    loading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.statusFilter.length > 0) requestParams.status__in = ui.statusFilter.join(',')
      if (ui.reviewedByFilter.length > 0)
        requestParams.reviewed_by__in = ui.reviewedByFilter.join(',')
      if (ui.dateFrom) requestParams.created_after = ui.dateFrom
      if (ui.dateTo) requestParams.created_before = ui.dateTo

      const response = await authAPI.getApplications(requestParams)
      applications.value = response.data.results || response.data
      total.value = response.data.count || applications.value.length
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Загрузить заявку по ID
  const fetchApplication = async (id) => {
    loading.value = true
    try {
      const response = await authAPI.getApplication(id)
      currentApplication.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Рассмотреть заявку (одобрить/отклонить)
  const reviewApplication = async (id, data) => {
    loading.value = true
    try {
      const response = await authAPI.reviewApplication(id, data)
      if (response.data.message) toast.success(response.data.message)
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Одобрить заявку
  const approveApplication = async (id, data) => {
    return await reviewApplication(id, { ...data, status: 'предоставлен' })
  }

  // Отклонить заявку
  const rejectApplication = async (id, comment) => {
    return await reviewApplication(id, { status: 'отклонён', review_comment: comment })
  }

  // Обновить заявку (полное)
  const updateApplication = async (id, data) => {
    loading.value = true
    try {
      const response = await authAPI.updateApplication(id, data)
      toast.success('Успешное изменение данных заявки')
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Обновить заявку (частичное)
  const updateApplicationPartial = async (id, data) => {
    loading.value = true
    try {
      const response = await authAPI.partialUpdateApplication(id, data)
      toast.success('Успешное изменение данных заявки')
      return { success: true, data: response.data }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Удалить заявку
  const deleteApplication = async (id) => {
    loading.value = true
    try {
      await authAPI.deleteApplication(id)
      toast.success('Успешное удаление заявки')
      return { success: true }
    } catch {
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // Проверить статус заявки по email
  const checkApplicationStatus = async (email) => {
    loading.value = true
    try {
      const response = await authAPI.checkApplicationStatus({ email })
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Подать заявку на регистрацию
  const submitApplication = async (data) => {
    loading.value = true
    try {
      const response = await authAPI.registerApplication(data)
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
    applications.value = []
    currentApplication.value = null
    total.value = 0
  }

  return {
    applications,
    currentApplication,
    loading,
    total,
    ui,
    getUIState,
    setUIState,

    fetchApplications,
    fetchApplication,
    reviewApplication,
    approveApplication,
    rejectApplication,
    updateApplication,
    updateApplicationPartial,
    deleteApplication,
    checkApplicationStatus,
    submitApplication,
    resetState,
  }
})
