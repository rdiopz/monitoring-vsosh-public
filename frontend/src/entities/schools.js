import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useSchoolsStore = defineStore('schools', () => {
  const toast = useToast()

  // Данные
  const schools = ref([])
  const isLoading = ref(false)
  const total = ref(0)

  // Опции для фильтров (загружаются с сервера)
  const filters = ref({
    municipalities: [],
  })

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'manage',
    search: '',
    sortBy: 'full_name',
    sortOrder: 'asc',
    municipalityFilter: [],
    visibleColumns: ['institution_id', 'municipality_name', 'full_name', 'short_name'],
    page: 1,
    pageSize: 20,
    addFormOpen: false,
    importOpen: true,
    exportOpen: true,
    exportColumns: ['institution_id', 'municipality_name', 'full_name', 'short_name'],
    exportWithFilters: false,
  })

  // Загрузить школы
  const fetchSchools = async (params = {}) => {
    isLoading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.municipalityFilter.length > 0) {
        requestParams.municipality__in = ui.municipalityFilter.join(',')
      }

      const response = await vsoshAPI.getSchools(requestParams)
      schools.value = response.data.results || response.data
      total.value = response.data.count || schools.value.length

      return response.data
    } catch (error) {
      console.error('Ошибка загрузки образовательных учреждений:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Получить фильтры
  const fetchFilters = async () => {
    try {
      const response = await vsoshAPI.getSchoolFilters()
      filters.value = response.data
      return response.data
    } catch (error) {
      console.error('Ошибка загрузки фильтров:', error)
    }
  }

  // Создать школу
  const createSchool = async (data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.createSchool(data)
      toast.success(response.data.message)
      await fetchSchools()
      return response.data
    } catch (error) {
      console.error('Ошибка создания образовательного учреждения:', error)
    } finally {
      isLoading.value = false
    }
  }

  // Обновить школу
  const updateSchool = async (id, data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.partialUpdateSchool(id, data)
      toast.success(response.data.message)
      await fetchSchools()
      return response.data
    } catch (error) {
      console.error('Ошибка обновления образовательного учреждения:', error)
    } finally {
      isLoading.value = false
    }
  }

  // Удалить школу
  const deleteSchool = async (id) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.deleteSchool(id)
      toast.success('Образовательное учреждение успешно удалено')
      await fetchSchools()
      return response.data
    } catch (error) {
      console.error('Ошибка удаления образовательного учреждения:', error)
    } finally {
      isLoading.value = false
    }
  }

  // Экспорт школ
  const exportSchools = async (columns = [], withFilters = false) => {
    isLoading.value = true
    try {
      const selectedColumns = columns.length > 0 ? columns : ui.exportColumns
      const params = { columns: selectedColumns }

      if (withFilters) {
        if (ui.search) params.search = ui.search
        if (ui.municipalityFilter.length > 0) {
          params.municipality__in = ui.municipalityFilter.join(',')
        }
        params.ordering = `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`
      }

      const response = await vsoshAPI.exportSchools(params)
      downloadFile(response, 'образовательные_учреждения.xlsx', toast)
    } catch (error) {
      console.error('Ошибка экспорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Импорт школ
  const importSchools = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await vsoshAPI.importSchools(formData)
      toast.success(response.data.message)
      await fetchSchools()
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
    schools.value = []
    total.value = 0
  }

  return {
    schools,
    isLoading,
    total,
    filters,
    ui,
    getUIState,
    setUIState,

    fetchSchools,
    fetchFilters,
    createSchool,
    updateSchool,
    deleteSchool,
    exportSchools,
    importSchools,
    resetState,
  }
})
