import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { vsoshAPI } from '@services/api'
import { downloadFile } from '@utils/download'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useReportsStore = defineStore('reports', () => {
  const toast = useToast()

  // Данные
  const reports = ref([])
  const isLoading = ref(false)
  const generatingKey = ref(null)

  // UI-состояние секции — сохраняется в URL
  const { ui, getUIState, setUIState } = useUIState({
    yearFilter: [],
    stageFilter: [],
    statusFilter: [],
    subjectFilter: [],
    municipalityFilter: [],
    educationFilter: [],
    filtersExtended: false,
  })

  // Собираем параметры запроса напрямую из ui
  const buildFilterParams = () => {
    const params = {}

    if (ui.yearFilter.length) params.year = ui.yearFilter
    if (ui.stageFilter.length) params.stage = ui.stageFilter
    if (ui.statusFilter.length) params.status = ui.statusFilter
    if (ui.subjectFilter.length) params.subject_id = ui.subjectFilter
    if (ui.municipalityFilter.length) params.municipality_id = ui.municipalityFilter
    if (ui.educationFilter.length) params.education_id = ui.educationFilter

    return params
  }
  // Получаем список отчетов
  const fetchReports = async () => {
    isLoading.value = true

    try {
      const response = await vsoshAPI.getReportsList()
      reports.value = response.data
    } catch (error) {
      console.error('Ошибка загрузки списка отчётов:', error)
      toast.error('Не удалось загрузить список отчётов')
    } finally {
      isLoading.value = false
    }
  }
  // Сформировать отчёт
  const generateReport = async (reportKey, filename) => {
    generatingKey.value = reportKey

    try {
      const params = buildFilterParams()
      const response = await vsoshAPI.generateReport(reportKey, params)
      downloadFile(response, filename, toast)
      toast.success('Отчёт сформирован')
    } catch (error) {
      console.error('Ошибка генерации отчёта:', error)
    } finally {
      generatingKey.value = null
    }
  }

  // Сбросить состояния
  const resetFilters = () => {
    ui.yearFilter = []
    ui.stageFilter = []
    ui.statusFilter = []
    ui.subjectFilter = []
    ui.municipalityFilter = []
    ui.educationFilter = []
  }

  return {
    reports,
    isLoading,
    generatingKey,
    ui,
    getUIState,
    setUIState,

    fetchReports,
    generateReport,
    resetFilters,
  }
})
