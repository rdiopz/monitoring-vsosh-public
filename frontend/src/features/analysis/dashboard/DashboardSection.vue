<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useDashboardStore } from '@entities/dashboard'
import { useOlympiadsStore } from '@entities/olympiads'
import { useSectionState } from '@composables/useSectionState.js'
import { participantOptionLabel } from '@utils/participants'
import { formatDateWithAge } from '@/shared/lib/utils/date.js'

import BaseTabs from '@ui/BaseTabs.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'
import SearchParticipants from '@/widgets/SearchParticipants/SearchParticipants.vue'

// Общие чарты
import DashboardSummary from './components/DashboardSummary.vue'
import DashboardStageChart from './components/charts/DashboardStageChart.vue'
import DashboardYearChart from './components/charts/DashboardYearChart.vue'
import DashboardStatusChart from './components/charts/DashboardStatusChart.vue'
import DashboardGenderChart from './components/charts/DashboardGenderChart.vue'
import DashboardSubjectChart from './components/charts/DashboardSubjectChart.vue'
import DashboardMunicipalityChart from './components/charts/DashboardMunicipalityChart.vue'
import DashboardClassChart from './components/charts/DashboardClassChart.vue'
import DashboardEducationChart from './components/charts/DashboardEducationChart.vue'

// Чарты участника
import ParticipantSummary from './components/ParticipantSummary.vue'
import ParticipantYearChart from './components/participant/ParticipantYearChart.vue'
import ParticipantStageChart from './components/participant/ParticipantStageChart.vue'
import ParticipantSubjectChart from './components/participant/ParticipantSubjectChart.vue'
import ParticipantStatusChart from './components/participant/ParticipantStatusChart.vue'
import ParticipantTable from './components/participant/ParticipantTable.vue'

const dashboardStore = useDashboardStore()
const olympiadsStore = useOlympiadsStore()

useSectionState('dashboard', dashboardStore)

const tabs = [
  { value: 'stats', label: 'Показатели' },
  { value: 'participant', label: 'Участник' },
]

const localYear = ref([])
const localStage = ref([])
const localStatus = ref([])
const localSubjectGroup = ref([])
const localSubject = ref([])
const localMunicipality = ref([])
const localEducation = ref([])
const localClass = ref([])
const localGender = ref([])

const yearOptions = computed(() =>
  (olympiadsStore.filters.years || []).map((y) => ({ label: String(y), value: y })),
)

const stageOptions = [
  { label: 'Школьный (ШЭ)', value: 'ШЭ' },
  { label: 'Муниципальный (МЭ)', value: 'МЭ' },
  { label: 'Региональный (РЭ)', value: 'РЭ' },
  { label: 'Заключительный (ЗЭ)', value: 'ЗЭ' },
]

const subjectGroupOptions = [
  { label: 'ВсОШ', value: 'vsosh' },
  { label: 'Олимпиада', value: 'olympiad' },
]

const statusOptions = [
  { label: 'Победитель', value: 'победитель' },
  { label: 'Призёр', value: 'призёр' },
  { label: 'Участник', value: 'участник' },
]

const genderOptions = [
  { label: 'М', value: 'М' },
  { label: 'Ж', value: 'Ж' },
]

const classOptions = computed(() =>
  (olympiadsStore.filters.classes || []).map((c) => ({ label: String(c), value: c })),
)

const municipalityOptions = computed(() =>
  (olympiadsStore.filters.municipalities || []).map((m) => ({
    label: m.name,
    value: m.municipality_id,
  })),
)

// Категория -> Предмет
const getSubjectCategory = (s) => (s.full_name?.startsWith('Олимпиада') ? 'olympiad' : 'vsosh')

const subjectOptions = computed(() => {
  let subjects = olympiadsStore.filters.subjects || []

  if (localSubjectGroup.value.length === 1) {
    subjects = subjects.filter((s) => localSubjectGroup.value.includes(getSubjectCategory(s)))
  }

  return subjects.map((s) => ({ label: s.full_name, value: s.subject_id }))
})

// Муниципалитет -> Учреждение
const educationOptions = computed(() => {
  let educations = olympiadsStore.filters.educations || []

  if (localMunicipality.value.length > 0) {
    educations = educations.filter((e) => localMunicipality.value.includes(e.municipality))
  }

  return educations.map((e) => ({ label: e.full_name, value: e.institution_id }))
})

// Очистка при смене зависимостей
watch(subjectOptions, (opts) => {
  const ids = new Set(opts.map((o) => o.value))
  localSubject.value = localSubject.value.filter((id) => ids.has(id))
})

watch(educationOptions, (opts) => {
  const ids = new Set(opts.map((o) => o.value))
  localEducation.value = localEducation.value.filter((id) => ids.has(id))
})

const handleApply = () => {
  dashboardStore.ui.yearFilter = [...localYear.value]
  dashboardStore.ui.stageFilter = [...localStage.value]
  dashboardStore.ui.statusFilter = [...localStatus.value]
  dashboardStore.ui.subjectGroupFilter = [...localSubjectGroup.value]
  dashboardStore.ui.subjectFilter = [...localSubject.value]
  dashboardStore.ui.municipalityFilter = [...localMunicipality.value]
  dashboardStore.ui.educationFilter = [...localEducation.value]
  dashboardStore.ui.classFilter = [...localClass.value]
  dashboardStore.ui.genderFilter = [...localGender.value]
  dashboardStore.fetchDashboard()
}

const handleReset = () => {
  localYear.value = []
  localStage.value = []
  localStatus.value = []
  localSubjectGroup.value = []
  localSubject.value = []
  localMunicipality.value = []
  localEducation.value = []
  localClass.value = []
  localGender.value = []
  dashboardStore.ui.yearFilter = []
  dashboardStore.ui.stageFilter = []
  dashboardStore.ui.statusFilter = []
  dashboardStore.ui.subjectGroupFilter = []
  dashboardStore.ui.subjectFilter = []
  dashboardStore.ui.municipalityFilter = []
  dashboardStore.ui.educationFilter = []
  dashboardStore.ui.classFilter = []
  dashboardStore.ui.genderFilter = []
  dashboardStore.fetchDashboard()
}

const localPYear = ref([])
const localPStage = ref([])
const localPStatus = ref([])
const localPSubject = ref([])
const localPClass = ref([])
const selectedParticipant = ref(null)

const pSubjectOptions = computed(() =>
  (olympiadsStore.filters.subjects || []).map((s) => ({
    label: s.full_name,
    value: s.subject_id,
  })),
)

const participantInitialOption = computed(() => {
  if (!dashboardStore.ui.participantId || !dashboardStore.ui.participantDisplay) return null
  return {
    value: Number(dashboardStore.ui.participantId),
    label: dashboardStore.ui.participantDisplay,
  }
})

// Участник: действия
const handleParticipantSelected = (participant) => {
  if (!participant) {
    selectedParticipant.value = null
    dashboardStore.clearParticipant()
    return
  }

  selectedParticipant.value = participant.participant_id
  dashboardStore.selectParticipant(participant.participant_id, participantOptionLabel(participant))
}

const handlePApply = () => {
  dashboardStore.ui.participantYearFilter = [...localPYear.value]
  dashboardStore.ui.participantStageFilter = [...localPStage.value]
  dashboardStore.ui.participantStatusFilter = [...localPStatus.value]
  dashboardStore.ui.participantSubjectFilter = [...localPSubject.value]
  dashboardStore.ui.participantClassFilter = [...localPClass.value]

  if (dashboardStore.ui.participantId) {
    dashboardStore.fetchParticipantDashboard(dashboardStore.ui.participantId)
  }
}

const handlePReset = () => {
  localPYear.value = []
  localPStage.value = []
  localPStatus.value = []
  localPSubject.value = []
  localPClass.value = []
  dashboardStore.ui.participantYearFilter = []
  dashboardStore.ui.participantStageFilter = []
  dashboardStore.ui.participantStatusFilter = []
  dashboardStore.ui.participantSubjectFilter = []
  dashboardStore.ui.participantClassFilter = []

  if (dashboardStore.ui.participantId) {
    dashboardStore.fetchParticipantDashboard(dashboardStore.ui.participantId)
  }
}

// Инициализация
onMounted(async () => {
  // Восстанавливаем локальные фильтры общего дашборда
  localYear.value = [...dashboardStore.ui.yearFilter]
  localStage.value = [...dashboardStore.ui.stageFilter]
  localStatus.value = [...dashboardStore.ui.statusFilter]
  localSubjectGroup.value = [...dashboardStore.ui.subjectGroupFilter]
  localSubject.value = [...dashboardStore.ui.subjectFilter]
  localMunicipality.value = [...dashboardStore.ui.municipalityFilter]
  localEducation.value = [...dashboardStore.ui.educationFilter]
  localClass.value = [...dashboardStore.ui.classFilter]
  localGender.value = [...dashboardStore.ui.genderFilter]

  // Восстанавливаем локальные фильтры участника
  localPYear.value = [...dashboardStore.ui.participantYearFilter]
  localPStage.value = [...dashboardStore.ui.participantStageFilter]
  localPStatus.value = [...dashboardStore.ui.participantStatusFilter]
  localPSubject.value = [...dashboardStore.ui.participantSubjectFilter]
  localPClass.value = [...dashboardStore.ui.participantClassFilter]

  if (!olympiadsStore.filters.years?.length) {
    await olympiadsStore.fetchFilters()
  }

  await dashboardStore.fetchDashboard()

  // Восстанавливаем выбранного участника
  if (dashboardStore.ui.participantId) {
    selectedParticipant.value = Number(dashboardStore.ui.participantId)
    await dashboardStore.fetchParticipantDashboard(dashboardStore.ui.participantId)
  }
})
</script>

<template>
  <div class="dashboard-section">
    <BaseTabs v-model="dashboardStore.ui.tab" :tabs="tabs" />

    <!-- Таб: Показатели -->
    <div v-show="dashboardStore.ui.tab === 'stats'" class="dashboard-tab">
      <FiltersPanel
        layout="stacked"
        :columns="14"
        :loading="dashboardStore.isLoading"
        :extended="dashboardStore.ui.filtersExtended"
        @update:extended="dashboardStore.ui.filtersExtended = $event"
        @apply="handleApply"
        @reset="handleReset"
      >
        <template #primary>
          <BaseMultiSelect
            v-model="localYear"
            placeholder="Год"
            :options="yearOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localStage"
            placeholder="Этап"
            :options="stageOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localStatus"
            placeholder="Статус"
            :options="statusOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localSubjectGroup"
            placeholder="Категория"
            :options="subjectGroupOptions"
            height="44px"
            class="compact"
          />
          <BaseMultiSelect
            v-model="localSubject"
            placeholder="Предмет"
            :options="subjectOptions"
            height="44px"
          />
        </template>

        <template #extended>
          <BaseMultiSelect
            v-model="localMunicipality"
            placeholder="Муниципалитет"
            :options="municipalityOptions"
            height="44px"
            class="medium"
          />
          <BaseMultiSelect
            v-model="localEducation"
            placeholder="Учреждение"
            :options="educationOptions"
            height="44px"
            class="wide"
          />
          <BaseMultiSelect
            v-model="localClass"
            placeholder="Класс"
            :options="classOptions"
            height="44px"
            class="compact"
          />
          <BaseMultiSelect
            v-model="localGender"
            placeholder="Пол"
            :options="genderOptions"
            height="44px"
            class="compact"
          />
        </template>
      </FiltersPanel>

      <template v-if="dashboardStore.data">
        <DashboardSummary :data="dashboardStore.data.summary" />

        <div class="charts-grid">
          <DashboardStageChart :data="dashboardStore.data.by_stage" />
          <DashboardYearChart :data="dashboardStore.data.by_year" />
          <DashboardStatusChart :data="dashboardStore.data.by_status" />
          <DashboardGenderChart :data="dashboardStore.data.by_gender" />
          <DashboardClassChart :data="dashboardStore.data.by_class" />
          <DashboardEducationChart :data="dashboardStore.data.by_education" />
          <DashboardSubjectChart :data="dashboardStore.data.by_subject" class="chart-wide" />
          <DashboardMunicipalityChart
            :data="dashboardStore.data.by_municipality"
            class="chart-wide"
          />
        </div>
      </template>
    </div>

    <!-- Таб: Участник  -->
    <div v-show="dashboardStore.ui.tab === 'participant'" class="dashboard-tab">
      <div class="participant-search-block">
        <div class="participant-search-head">
          <span class="participant-search-title">Выберите участника</span>
          <span class="participant-search-hint"> Введите ФИО или дату рождения для поиска </span>
        </div>

        <SearchParticipants
          v-model="selectedParticipant"
          :initial-option="participantInitialOption"
          placeholder="ФИО или дата рождения..."
          @selected="handleParticipantSelected"
        />
      </div>

      <template v-if="dashboardStore.ui.participantId">
        <FiltersPanel
          :loading="dashboardStore.isParticipantLoading"
          @apply="handlePApply"
          @reset="handlePReset"
        >
          <template #primary>
            <BaseMultiSelect
              v-model="localPYear"
              placeholder="Год"
              :options="yearOptions"
              height="44px"
            />
            <BaseMultiSelect
              v-model="localPStage"
              placeholder="Этап"
              :options="stageOptions"
              height="44px"
            />
            <BaseMultiSelect
              v-model="localPStatus"
              placeholder="Статус"
              :options="statusOptions"
              height="44px"
            />
            <BaseMultiSelect
              v-model="localPSubject"
              placeholder="Предмет"
              :options="pSubjectOptions"
              height="44px"
            />
          </template>
        </FiltersPanel>

        <!-- Карточка участника -->
        <div v-if="dashboardStore.participantData?.participant" class="participant-card">
          <div class="participant-card-row">
            <span class="participant-card-label">ФИО</span>
            <span class="participant-card-value">
              {{ dashboardStore.participantData.participant.full_name }}
            </span>
          </div>
          <div class="participant-card-row">
            <span class="participant-card-label">Дата рождения</span>
            <span class="participant-card-value">
              {{ formatDateWithAge(dashboardStore.participantData.participant.birth_date) }}
            </span>
          </div>
          <div class="participant-card-row">
            <span class="participant-card-label">Пол</span>
            <span class="participant-card-value">
              {{ dashboardStore.participantData.participant.gender }}
            </span>
          </div>
        </div>

        <!-- Аналитика участника -->
        <template v-if="dashboardStore.participantData">
          <ParticipantSummary :data="dashboardStore.participantData.summary" />

          <div class="charts-grid">
            <ParticipantYearChart :data="dashboardStore.participantData.by_year" />
            <ParticipantStageChart :data="dashboardStore.participantData.by_stage" />
            <ParticipantStatusChart :data="dashboardStore.participantData.by_status" />
            <ParticipantSubjectChart :data="dashboardStore.participantData.by_subject" />
          </div>

          <ParticipantTable :data="dashboardStore.participantData.participations" />
        </template>
      </template>

      <div v-else class="dashboard-empty">
        <p class="dashboard-placeholder">Выберите участника, чтобы увидеть аналитику</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-section {
  width: 100%;
  background: var(--white);
  border-radius: 12px;
}

.dashboard-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 40px 40px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.dashboard-placeholder {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  font: var(--common-text);
}

/* Сетка графиков: 2 в ряд */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

/* Широкий чарт — на всю ширину */
.charts-grid > .chart-wide {
  grid-column: 1 / -1;
}

.participant-search-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--white);
}

.participant-search-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.participant-search-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
}

.participant-search-hint {
  font: var(--common-text);
  color: var(--text-secondary);
}

/* Карточка участника */
.participant-card {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 32px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-background-soft);
}

.participant-card-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.participant-card-label {
  font: var(--tiny-text);
  color: var(--text-tertiary);
  font-weight: 500;
}

.participant-card-value {
  font: var(--common-text);
  color: var(--text-primary);
  font-weight: 600;
}

@media (max-width: 960px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-tab {
    padding: 16px 20px 20px;
  }
}
</style>
