import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useMunicipalitiesStore = defineStore('municipalities', () => {
  const toast = useToast()

  // Данные
  const municipalities = ref([])
  const isLoading = ref(false)
  const total = ref(0)

  // Сортировка
  const sortBy = ref('name')

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'manage',
    search: '',
    sortOrder: 'asc',
    addFormOpen: false,
    importOpen: true,
    exportOpen: true,
    exportColumns: ['municipality_id', 'name'],
    exportWithFilters: false,
  })

  // Загрузить муниципалитеты
  const fetchMunicipalities = async (params = {}) => {
    isLoading.value = true
    try {
      const requestParams = {
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${sortBy.value}`,
        ...params,
      }

      const response = await vsoshAPI.getMunicipalities(requestParams)
      municipalities.value = response.data.results || response.data
      total.value = response.data.count || municipalities.value.length

      return response.data
    } catch (error) {
      console.error('Ошибка загрузки муниципалитетов:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Создать муниципалитет
  const createMunicipality = async (data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.createMunicipality(data)
      toast.success(response.data.message)
      await fetchMunicipalities()
      return response.data
    } catch (error) {
      console.error('Ошибка создания муниципалитета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Обновить муниципалитет
  const updateMunicipality = async (id, data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.partialUpdateMunicipality(id, data)
      toast.success(response.data.message)
      await fetchMunicipalities()
      return response.data
    } catch (error) {
      console.error('Ошибка обновления муниципалитета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Удалить муниципалитет
  const deleteMunicipality = async (id) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.deleteMunicipality(id)
      toast.success('Муниципалитет успешно удален')
      await fetchMunicipalities()
      return response.data
    } catch (error) {
      console.error('Ошибка удаления муниципалитета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Экспорт муниципалитетов
  const exportMunicipalities = async (columns = [], withFilters = false) => {
    isLoading.value = true
    try {
      const selectedColumns = columns.length > 0 ? columns : ui.exportColumns
      const params = { columns: selectedColumns }

      if (withFilters) {
        if (ui.search) params.search = ui.search
        params.ordering = `${ui.sortOrder === 'asc' ? '' : '-'}${sortBy.value}`
      }

      const response = await vsoshAPI.exportMunicipalities(params)
      downloadFile(response, 'муниципалитеты.xlsx', toast)
    } catch (error) {
      console.error('Ошибка экспорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Импорт муниципалитетов
  const importMunicipalities = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await vsoshAPI.importMunicipalities(formData)
      toast.success(response.data.message)
      await fetchMunicipalities()
      return response.data
    } catch (error) {
      console.error('Ошибка импорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Переключить сортировку
  const toggleSort = () => {
    ui.sortOrder = ui.sortOrder === 'asc' ? 'desc' : 'asc'
    fetchMunicipalities()
  }

  // Сбросить состояние
  const resetState = () => {
    municipalities.value = []
    total.value = 0
  }

  return {
    municipalities,
    isLoading,
    total,
    sortBy,
    ui,
    getUIState,
    setUIState,

    fetchMunicipalities,
    createMunicipality,
    updateMunicipality,
    deleteMunicipality,
    exportMunicipalities,
    importMunicipalities,
    toggleSort,
    resetState,
  }
})
