import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useOlympiadsStore = defineStore('olympiads', () => {
  const toast = useToast()

  // Данные
  const participations = ref([])
  const isLoading = ref(false)
  const total = ref(0)

  // Опции для фильтров (загружаются с сервера)
  const filters = ref({
    stages: [],
    statuses: [],
    genders: [],
    classes: [],
    years: [],
    subjects: [],
    educations: [],
    municipalities: [],
  })

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'manage',
    search: '',
    sortBy: 'year',
    sortOrder: 'desc',
    stageFilter: [],
    statusFilter: [],
    classFilter: [],
    yearFilter: [],
    subjectFilter: [],
    municipalityFilter: [],
    educationFilter: [],
    genderFilter: [],
    filtersExtended: false,
    visibleColumns: [
      'olymp_id',
      'participant_full_name',
      'municipality_name',
      'education_short_name',
      'subject_short_name',
      'class_field',
      'stage',
      'status',
      'year',
    ],
    page: 1,
    pageSize: 20,
    addFormOpen: false,
    importOpen: true,
    exportOpen: true,
    exportColumns: [
      'olymp_id',
      'participant_lastname',
      'participant_firstname',
      'participant_patronymic',
      'participant_birth_date',
      'participant_gender',
      'municipality_name',
      'education_institution_name',
      'education_short_name',
      'subject_full_name',
      'class_field',
      'stage',
      'status',
      'year',
    ],
    exportWithFilters: false,
  })

  // Загрузить участия
  const fetchParticipations = async (params = {}) => {
    isLoading.value = true
    try {
      const requestParams = {
        page: params.page || ui.page,
        page_size: params.pageSize || ui.pageSize,
        search: params.search || ui.search,
        ordering: params.ordering || `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`,
        ...params,
      }

      if (ui.stageFilter.length > 0) requestParams.stage__in = ui.stageFilter.join(',')
      if (ui.statusFilter.length > 0) requestParams.status__in = ui.statusFilter.join(',')
      if (ui.classFilter.length > 0) requestParams.class_field__in = ui.classFilter.join(',')
      if (ui.yearFilter.length > 0) requestParams.year__in = ui.yearFilter.join(',')
      if (ui.subjectFilter.length > 0) requestParams.subject__in = ui.subjectFilter.join(',')
      if (ui.municipalityFilter.length > 0)
        requestParams.municipality__in = ui.municipalityFilter.join(',')
      if (ui.educationFilter.length > 0) requestParams.education__in = ui.educationFilter.join(',')
      if (ui.genderFilter.length > 0) requestParams.gender__in = ui.genderFilter.join(',')

      const response = await vsoshAPI.getOlympiadParticipations(requestParams)
      participations.value = response.data.results || response.data
      total.value = response.data.count || participations.value.length

      return response.data
    } catch (error) {
      console.error('Ошибка загрузки участий в олимпиаде:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Загрузить фильтры
  const fetchFilters = async () => {
    try {
      const response = await vsoshAPI.getOlympiadFilters()
      filters.value = response.data
      return response.data
    } catch (error) {
      console.error('Ошибка загрузки фильтров:', error)
      throw error
    }
  }

  // Создать участие
  const createParticipation = async (data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.createOlympiadParticipation(data)
      toast.success(response.data.message)
      await fetchParticipations()
      return response.data
    } catch (error) {
      console.error('Ошибка создания участия:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Обновить участие
  const updateParticipation = async (id, data) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.partialUpdateOlympiadParticipation(id, data)
      toast.success(response.data.message)
      await fetchParticipations()
      return response.data
    } catch (error) {
      console.error('Ошибка обновления участия:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Удалить участие
  const deleteParticipation = async (id) => {
    isLoading.value = true
    try {
      const response = await vsoshAPI.deleteOlympiadParticipation(id)
      toast.success('Участие в олимпиаде успешно удалено')
      await fetchParticipations()
      return response.data
    } catch (error) {
      console.error('Ошибка удаления участия:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Экспорт участий
  const exportParticipations = async (columns = [], withFilters = false) => {
    isLoading.value = true
    try {
      const selectedColumns = columns.length > 0 ? columns : ui.exportColumns
      const params = { columns: selectedColumns }

      if (withFilters) {
        if (ui.search) params.search = ui.search
        if (ui.stageFilter.length > 0) params.stage__in = ui.stageFilter.join(',')
        if (ui.statusFilter.length > 0) params.status__in = ui.statusFilter.join(',')
        if (ui.classFilter.length > 0) params.class_field__in = ui.classFilter.join(',')
        if (ui.yearFilter.length > 0) params.year__in = ui.yearFilter.join(',')
        if (ui.subjectFilter.length > 0) params.subject__in = ui.subjectFilter.join(',')
        if (ui.municipalityFilter.length > 0)
          params.municipality__in = ui.municipalityFilter.join(',')
        if (ui.educationFilter.length > 0) params.education__in = ui.educationFilter.join(',')
        if (ui.genderFilter.length > 0) params.gender__in = ui.genderFilter.join(',')
        params.ordering = `${ui.sortOrder === 'asc' ? '' : '-'}${ui.sortBy}`
      }

      const response = await vsoshAPI.exportOlympiadParticipations(params)
      downloadFile(response, 'участие_в_олимпиаде.xlsx', toast)
    } catch (error) {
      console.error('Ошибка экспорта:', error)
    } finally {
      isLoading.value = false
    }
  }

  // Импорт участий
  const importParticipations = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await vsoshAPI.importOlympiadParticipations(formData)
      toast.success(response.data.message)
      await fetchParticipations()
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
    participations.value = []
    total.value = 0
  }

  return {
    participations,
    isLoading,
    total,
    filters,
    ui,
    getUIState,
    setUIState,

    fetchParticipations,
    fetchFilters,
    createParticipation,
    updateParticipation,
    deleteParticipation,
    exportParticipations,
    importParticipations,
    resetState,
  }
})
