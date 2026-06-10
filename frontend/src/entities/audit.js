import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@services/api'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useAuditStore = defineStore('audit', () => {
  // Данные
  const auditLogs = ref([])
  const currentLog = ref(null)
  const loading = ref(false)
  const total = ref(0)

  // Опции фильтров (загружаются с сервера)
  const actionOptions = ref([])
  const modelOptions = ref([])

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    search: '',
    sortBy: 'timestamp',
    sortOrder: 'desc',
    actionFilter: [],
    modelFilter: [],
    dateFrom: null,
    dateTo: null,
    objectIdFilter: '',
    filtersExtended: false,
    visibleColumns: [
      'log_id',
      'timestamp',
      'user_email',
      'action',
      'model_name',
      'object_id',
      'ip_address',
    ],
    expandedRows: [],
    page: 1,
    pageSize: 20,
  })

  // Загрузить опции фильтров
  const fetchFilterOptions = async () => {
    const response = await authAPI.getAuditLogFilters()
    actionOptions.value = (response.data.actions || []).map((action) => ({
      label: action,
      value: action,
    }))
    modelOptions.value = (response.data.models || []).map((model) => ({
      label: model,
      value: model,
    }))
    return response.data
  }

  // Загрузить логи аудита
  const fetchAuditLogs = async (params = {}) => {
    loading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.actionFilter.length > 0) requestParams.action__in = ui.actionFilter.join(',')
      if (ui.modelFilter.length > 0) requestParams.model_name__in = ui.modelFilter.join(',')
      if (ui.dateFrom) requestParams.timestamp_from = ui.dateFrom
      if (ui.dateTo) requestParams.timestamp_to = ui.dateTo
      if (ui.objectIdFilter) requestParams.object_id = ui.objectIdFilter

      const response = await authAPI.getAuditLogs(requestParams)
      auditLogs.value = response.data.results || response.data
      total.value = response.data.count || auditLogs.value.length
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Загрузить лог по ID
  const fetchAuditLog = async (id) => {
    loading.value = true
    try {
      const response = await authAPI.getAuditLog(id)
      currentLog.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Сбросить состояние
  const resetState = () => {
    auditLogs.value = []
    currentLog.value = null
    total.value = 0
  }

  return {
    auditLogs,
    currentLog,
    loading,
    total,
    actionOptions,
    modelOptions,
    ui,
    getUIState,
    setUIState,

    fetchAuditLogs,
    fetchAuditLog,
    fetchFilterOptions,
    resetState,
  }
})
