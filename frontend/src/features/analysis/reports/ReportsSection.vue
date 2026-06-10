<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useReportsStore } from '@entities/reports'
import { useOlympiadsStore } from '@entities/olympiads'
import { useSectionState } from '@composables/useSectionState.js'

import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseButton from '@ui/BaseButton.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import EmptyState from '@ui/EmptyState.vue'

const reportsStore = useReportsStore()
const olympiadsStore = useOlympiadsStore()

useSectionState('reports', reportsStore)

const searchQuery = ref('')

// Опции фильтров
const yearOptions = computed(() =>
  (olympiadsStore.filters.years || []).map((y) => ({ label: String(y), value: y })),
)

const stageOptions = [
  { label: 'Школьный (ШЭ)', value: 'ШЭ' },
  { label: 'Муниципальный (МЭ)', value: 'МЭ' },
  { label: 'Региональный (РЭ)', value: 'РЭ' },
  { label: 'Заключительный (ЗЭ)', value: 'ЗЭ' },
]

const statusOptions = [
  { label: 'Победитель', value: 'победитель' },
  { label: 'Призёр', value: 'призёр' },
  { label: 'Участник', value: 'участник' },
]

const subjectOptions = computed(() =>
  (olympiadsStore.filters.subjects || []).map((s) => ({
    label: s.full_name,
    value: s.subject_id,
  })),
)

const municipalityOptions = computed(() =>
  (olympiadsStore.filters.municipalities || []).map((m) => ({
    label: m.name,
    value: m.municipality_id,
  })),
)

// Муниципалитет -> Учреждение
const educationOptions = computed(() => {
  let educations = olympiadsStore.filters.educations || []

  if (reportsStore.ui.municipalityFilter.length > 0) {
    educations = educations.filter((e) =>
      reportsStore.ui.municipalityFilter.includes(e.municipality),
    )
  }

  return educations.map((e) => ({
    label: e.full_name,
    value: e.institution_id,
  }))
})

// Очищаем учреждения при смене муниципалитета
watch(educationOptions, (opts) => {
  const ids = new Set(opts.map((o) => o.value))
  reportsStore.ui.educationFilter = reportsStore.ui.educationFilter.filter((id) => ids.has(id))
})

const hasActiveFilters = computed(() => {
  return (
    reportsStore.ui.yearFilter.length > 0 ||
    reportsStore.ui.stageFilter.length > 0 ||
    reportsStore.ui.statusFilter.length > 0 ||
    reportsStore.ui.subjectFilter.length > 0 ||
    reportsStore.ui.municipalityFilter.length > 0 ||
    reportsStore.ui.educationFilter.length > 0
  )
})

// Фильтрация отчётов по поисковой строке
const filteredReports = computed(() => {
  if (!searchQuery.value) return reportsStore.reports

  const query = searchQuery.value.toLowerCase()

  return reportsStore.reports.filter(
    (r) => r.title.toLowerCase().includes(query) || r.description?.toLowerCase().includes(query),
  )
})

const handleReset = () => {
  reportsStore.resetFilters()
}

const handleGenerate = (report) => {
  reportsStore.generateReport(report.key, report.filename)
}

onMounted(async () => {
  if (!olympiadsStore.filters.years?.length) {
    await olympiadsStore.fetchFilters()
  }

  await reportsStore.fetchReports()
})
</script>

<template>
  <div class="reports-section">
    <FiltersPanel
      layout="inline"
      :columns="12"
      :extended="reportsStore.ui.filtersExtended"
      @update:extended="reportsStore.ui.filtersExtended = $event"
      @reset="handleReset"
    >
      <template #primary>
        <BaseMultiSelect
          v-model="reportsStore.ui.yearFilter"
          placeholder="Год"
          :options="yearOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="reportsStore.ui.stageFilter"
          placeholder="Этап"
          :options="stageOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="reportsStore.ui.statusFilter"
          placeholder="Статус"
          :options="statusOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="reportsStore.ui.subjectFilter"
          placeholder="Предмет"
          :options="subjectOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="reportsStore.ui.municipalityFilter"
          placeholder="Муниципалитет"
          :options="municipalityOptions"
          height="44px"
          class="medium"
        />
        <BaseMultiSelect
          v-model="reportsStore.ui.educationFilter"
          placeholder="Учреждение"
          :options="educationOptions"
          height="44px"
          class="large"
        />
      </template>
    </FiltersPanel>

    <div class="reports-filter-status">
      <span v-if="hasActiveFilters" class="filter-status-active">
        Отчёты будут сформированы с учётом выбранных фильтров
      </span>
      <span v-else class="filter-status-default"> Отчёты будут сформированы по всем данным </span>
    </div>

    <SearchBar v-model="searchQuery" placeholder="Поиск по названию отчёта..." />

    <BaseSpinner v-if="reportsStore.isLoading" text="Загрузка списка отчётов..." />

    <EmptyState v-else-if="reportsStore.reports.length === 0" message="Нет доступных отчётов" />

    <template v-else>
      <div v-if="filteredReports.length" class="reports-list">
        <div v-for="report in filteredReports" :key="report.key" class="report-card">
          <div class="report-card-body">
            <div class="report-card-info">
              <span class="report-card-title">{{ report.title }}</span>
              <p class="report-card-description">{{ report.description }}</p>
            </div>

            <div class="report-card-actions">
              <span class="report-card-format">XLSX</span>

              <BaseButton
                variant="primary"
                size="small"
                :loading="reportsStore.generatingKey === report.key"
                :disabled="
                  reportsStore.generatingKey !== null && reportsStore.generatingKey !== report.key
                "
                @click="handleGenerate(report)"
              >
                Сформировать
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <EmptyState v-else message="Отчёты не найдены" />
    </template>
  </div>
</template>

<style scoped>
.reports-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.reports-filter-status {
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--color-background-soft);
  border-left: 3px solid var(--color-border);
}

.filter-status-default {
  font: var(--common-text);
  color: var(--text-tertiary);
}

.filter-status-active {
  font: var(--common-text);
  color: var(--secondary);
  font-weight: 500;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-card {
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.report-card:hover {
  border-color: var(--secondary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.report-card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 20px 24px;
}

.report-card-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.report-card-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
}

.report-card-description {
  font: var(--common-text);
  color: var(--text-secondary);
  line-height: 1.5;
}

.report-card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.report-card-format {
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--color-background-soft);
  font: var(--tiny-text);
  color: var(--text-tertiary);
  font-weight: 600;
  letter-spacing: 0.05em;
}

@media (max-width: 768px) {
  .reports-section {
    padding: 16px;
  }

  .report-card-body {
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
    padding: 16px;
  }

  .report-card-actions {
    justify-content: space-between;
  }
}
</style>
