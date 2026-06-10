import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useParticipantsStore = defineStore('participants', () => {
  const toast = useToast()

  // Данные
  const participants = ref([])
  const isLoading = ref(false)
  const isSearching = ref(false)
  const total = ref(0)

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'manage',
    search: '',
    sortBy: 'full_name',
    sortOrder: 'asc',
    genderFilter: [],
    dateFrom: null,
    dateTo: null,
    filtersExtended: false,
    visibleColumns: ['participant_id', 'full_name', 'birth_date', 'gender'],
    page: 1,
    pageSize: 20,
    addFormOpen: false,
    importOpen: true,
    exportOpen: true,
    exportColumns: [
      'participant_id',
      'lastname',
      'firstname',
      'patronymic',
      'birth_date',
      'gender',
    ],
    exportWithFilters: false,
  })

  // Загрузить участников
  const fetchParticipants = async (params = {}) => {
    isLoading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.genderFilter.length > 0) {
        requestParams.gender__in = ui.genderFilter.join(',')
      }
      if (ui.dateFrom) requestParams.birth_date_after = ui.dateFrom
      if (ui.dateTo) requestParams.birth_date_before = ui.dateTo

      const response = await vsoshAPI.getParticipants(requestParams)
      participants.value = response.data.results || response.data
      total.value = response.data.count || participants.value.length

      return response.data
    } catch (error) {
      console.error('Ошибка загрузки участников:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Поиск участников для селектов и дашборда
  const searchParticipants = async (params = {}) => {
    isSearching.value = true
    try {
      const requestParams = {
        q: params.q ?? '',
        limit: params.limit ?? 20,
        offset: params.offset ?? 0,
        ...params,
      }

      const response = await vsoshAPI.searchParticipants(requestParams)
      return response.data
    } catch (error) {
      console.error('Ошибка поиска участников:', error)
      throw error
    } finally {
      isSearching.value = false
    }
  }

  // Создать участника
  const createParticipant = async (data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.createParticipant(data)
      toast.success(response.data.message)
      await fetchParticipants()
      return response.data
    } catch (error) {
      console.error('Ошибка создания участника:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Обновить участника
  const updateParticipant = async (id, data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.partialUpdateParticipant(id, data)
      toast.success(response.data.message)
      await fetchParticipants()
      return response.data
    } catch (error) {
      console.error('Ошибка обновления участника:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Удалить участника
  const deleteParticipant = async (id) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.deleteParticipant(id)
      toast.success('Участник успешно удален')
      await fetchParticipants()
      return response.data
    } catch (error) {
      console.error('Ошибка удаления участника:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Экспорт участников
  const exportParticipants = async (columns = [], withFilters = false) => {
    isLoading.value = true
    try {
      const selectedColumns = columns.length > 0 ? columns : ui.exportColumns
      const params = { columns: selectedColumns }

      if (withFilters) {
        if (ui.search) params.search = ui.search
        if (ui.genderFilter.length > 0) params.gender__in = ui.genderFilter.join(',')
        if (ui.dateFrom) params.birth_date_after = ui.dateFrom
        if (ui.dateTo) params.birth_date_before = ui.dateTo
        params.ordering = `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`
      }

      const response = await vsoshAPI.exportParticipants(params)
      downloadFile(response, 'участники.xlsx', toast)
    } catch (error) {
      console.error('Ошибка экспорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Импорт участников
  const importParticipants = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await vsoshAPI.importParticipants(formData)
      toast.success(response.data.message)
      await fetchParticipants()
      return response.data
    } catch (error) {
      console.error('Ошибка импорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Сбросить состояние
  const resetState = () => {
    participants.value = []
    total.value = 0
  }

  return {
    participants,
    isLoading,
    isSearching,
    total,
    ui,
    getUIState,
    setUIState,

    fetchParticipants,
    searchParticipants,
    createParticipant,
    updateParticipant,
    deleteParticipant,
    exportParticipants,
    importParticipants,
    resetState,
  }
})
