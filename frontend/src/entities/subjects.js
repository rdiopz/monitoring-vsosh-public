import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useSubjectsStore = defineStore('subjects', () => {
  const toast = useToast()

  // Данные
  const subjects = ref([])
  const isLoading = ref(false)
  const total = ref(0)

  // Сортировка
  const sortBy = ref('full_name')

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'manage',
    search: '',
    sortOrder: 'asc',
    addFormOpen: false,
    importOpen: true,
    exportOpen: true,
    exportColumns: ['subject_id', 'full_name', 'short_name'],
    exportWithFilters: false,
  })

  // Загрузить предметы
  const fetchSubjects = async (params = {}) => {
    isLoading.value = true
    try {
      const requestParams = {
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${sortBy.value}`,
        ...params,
      }

      const response = await vsoshAPI.getSubjects(requestParams)
      subjects.value = response.data.results || response.data
      total.value = response.data.count || subjects.value.length

      return response.data
    } catch (error) {
      console.error('Ошибка загрузки предметов:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Создать предмет
  const createSubject = async (data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.createSubject(data)
      toast.success(response.data.message)
      await fetchSubjects()
      return response.data
    } catch (error) {
      console.error('Ошибка создания предмета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Обновить предмет
  const updateSubject = async (id, data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.partialUpdateSubject(id, data)
      toast.success(response.data.message)
      await fetchSubjects()
      return response.data
    } catch (error) {
      console.error('Ошибка обновления предмета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Удалить предмет
  const deleteSubject = async (id) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.deleteSubject(id)
      toast.success('Предмет успешно удален')
      await fetchSubjects()
      return response.data
    } catch (error) {
      console.error('Ошибка удаления предмета:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Экспорт предметов
  const exportSubjects = async (columns = [], withFilters = false) => {
    isLoading.value = true
    try {
      const selectedColumns = columns.length > 0 ? columns : ui.exportColumns
      const params = { columns: selectedColumns }

      if (withFilters) {
        if (ui.search) params.search = ui.search
        params.ordering = `${ui.sortOrder === 'asc' ? '' : '-'}${sortBy.value}`
      }

      const response = await vsoshAPI.exportSubjects(params)
      downloadFile(response, 'предметы.xlsx', toast)
    } catch (error) {
      console.error('Ошибка экспорта:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Импорт предметов
  const importSubjects = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await vsoshAPI.importSubjects(formData)
      toast.success(response.data.message)
      await fetchSubjects()
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
    fetchSubjects()
  }

  // Сбросить состояние
  const resetState = () => {
    subjects.value = []
    total.value = 0
  }

  return {
    subjects,
    isLoading,
    total,
    sortBy,
    ui,
    getUIState,
    setUIState,

    fetchSubjects,
    createSubject,
    updateSubject,
    deleteSubject,
    exportSubjects,
    importSubjects,
    toggleSort,
    resetState,
  }
})
