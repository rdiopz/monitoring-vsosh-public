import { defineStore } from 'pinia'
import { ref } from 'vue'
import { vsoshAPI } from '@services/api'
import { useUIState } from '@/shared/lib/composables/useUIState'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(null)
  const isLoading = ref(false)

  const participantData = ref(null)
  const isParticipantLoading = ref(false)

  // Все фильтры лежат в ui и сохраняются в URL.
  const { ui, getUIState, setUIState } = useUIState({
    tab: 'stats',

    // Общий дашборд
    yearFilter: [],
    stageFilter: [],
    statusFilter: [],
    subjectGroupFilter: [],
    subjectFilter: [],
    municipalityFilter: [],
    educationFilter: [],
    classFilter: [],
    genderFilter: [],
    filtersExtended: false,

    // Участник
    participantId: null,
    participantDisplay: '',
    participantYearFilter: [],
    participantStageFilter: [],
    participantStatusFilter: [],
    participantSubjectFilter: [],
    participantClassFilter: [],
    participantFiltersExtended: false,
  })

  // Собираем параметры запроса общего дашборда
  const buildDashboardParams = () => {
    const params = {}

    if (ui.yearFilter.length) params.year = ui.yearFilter
    if (ui.stageFilter.length) params.stage = ui.stageFilter
    if (ui.statusFilter.length) params.status = ui.statusFilter
    if (ui.subjectGroupFilter.length) params.subject_group = ui.subjectGroupFilter
    if (ui.subjectFilter.length) params.subject_id = ui.subjectFilter
    if (ui.municipalityFilter.length) params.municipality_id = ui.municipalityFilter
    if (ui.educationFilter.length) params.education_id = ui.educationFilter
    if (ui.classFilter.length) params.class_field = ui.classFilter
    if (ui.genderFilter.length) params.gender = ui.genderFilter

    return params
  }

  // Собираем параметры запроса вкладки участника
  const buildParticipantParams = () => {
    const params = {}

    if (ui.participantYearFilter.length) params.year = ui.participantYearFilter
    if (ui.participantStageFilter.length) params.stage = ui.participantStageFilter
    if (ui.participantStatusFilter.length) params.status = ui.participantStatusFilter
    if (ui.participantSubjectFilter.length) params.subject_id = ui.participantSubjectFilter
    if (ui.participantClassFilter.length) params.class_field = ui.participantClassFilter

    return params
  }

  // Загружаем общий дашборд
  const fetchDashboard = async () => {
    isLoading.value = true

    try {
      const response = await vsoshAPI.getDashboard(buildDashboardParams())
      data.value = response.data
    } catch (error) {
      console.error('Ошибка загрузки дашборда:', error)
      data.value = null
    } finally {
      isLoading.value = false
    }
  }

  // Загружаем дашборд участника
  const fetchParticipantDashboard = async (participantId) => {
    if (!participantId) {
      participantData.value = null
      return
    }

    isParticipantLoading.value = true

    try {
      const response = await vsoshAPI.getParticipantDashboard(
        participantId,
        buildParticipantParams(),
      )
      participantData.value = response.data
      ui.participantId = participantId
    } catch (error) {
      console.error('Ошибка загрузки дашборда участника:', error)
      participantData.value = null
    } finally {
      isParticipantLoading.value = false
    }
  }

  // Сохраняем данные выбранного участника
  const selectParticipant = (participantId, participantDisplay = '') => {
    ui.participantId = participantId
    ui.participantDisplay = participantDisplay
    fetchParticipantDashboard(participantId)
  }

  // Очищаем данные участника
  const clearParticipant = () => {
    ui.participantId = null
    ui.participantDisplay = ''
    participantData.value = null
  }

  // Сбросить состояние
  const resetState = () => {
    data.value = null
    participantData.value = null
  }

  return {
    data,
    isLoading,
    participantData,
    isParticipantLoading,
    ui,
    getUIState,
    setUIState,

    fetchDashboard,
    fetchParticipantDashboard,
    selectParticipant,
    clearParticipant,
    resetState,
  }
})
