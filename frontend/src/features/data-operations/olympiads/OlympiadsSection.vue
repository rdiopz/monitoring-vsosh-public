<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOlympiadsStore } from '@entities/olympiads'
import { useSectionState } from '@composables/useSectionState.js'
import { formatDate, formatDateTime, calculateAge } from '@utils/date'

import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import ExportArea from '@/widgets/ExportArea/ExportArea.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'
import ImportArea from '@/widgets/ImportArea/ImportArea.vue'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import CopyHeaders from '@/widgets/CopyHeaders/CopyHeaders.vue'

import BaseCollapse from '@ui/BaseCollapse.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseTable from '@ui/BaseTable.vue'
import BaseColumnToggle from '@ui/BaseColumnToggle.vue'
import BasePagination from '@ui/BasePagination.vue'
import BaseTabs from '@ui/BaseTabs.vue'
import BaseTag from '@ui/BaseTag.vue'
import BaseScrollableCell from '@ui/BaseScrollableCell.vue'

import EditIcon from '@icons/actions/EditIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'

import OlympiadsAddDialog from './components/OlympiadsAddDialog.vue'
import OlympiadsEditDialog from './components/OlympiadsEditDialog.vue'

const olympiadsStore = useOlympiadsStore()

useSectionState('olympiads', olympiadsStore)

const localStageFilter = ref([])
const localStatusFilter = ref([])
const localClassFilter = ref([])
const localYearFilter = ref([])
const localSubjectFilter = ref([])
const localMunicipalityFilter = ref([])
const localEducationFilter = ref([])
const localGenderFilter = ref([])

const columns = [
  // Технический ID
  { key: 'olymp_id', label: 'ID', sortable: true, width: '70px', visible: true },

  // Основная информация об участнике
  { key: 'participant_full_name', label: 'ФИО', sortable: true, width: '300px', visible: true },
  { key: 'participant_lastname', label: 'Фамилия', sortable: true, width: '160px', visible: false },
  { key: 'participant_firstname', label: 'Имя', sortable: true, width: '140px', visible: false },
  {
    key: 'participant_patronymic',
    label: 'Отчество',
    sortable: true,
    width: '160px',
    visible: false,
  },
  {
    key: 'participant_birth_date',
    label: 'Дата рождения',
    sortable: true,
    width: '130px',
    visible: false,
  },
  { key: 'participant_gender', label: 'Пол', sortable: true, width: '70px', visible: false },

  // Предмет
  { key: 'subject_short_name', label: 'Предмет', sortable: true, width: '200px', visible: true },
  {
    key: 'subject_full_name',
    label: 'Полн. Предмет',
    sortable: true,
    width: '180px',
    visible: false,
  },

  // Учебный контекст
  { key: 'class_field', label: 'Класс', sortable: true, width: '70px', visible: true },
  { key: 'stage', label: 'Этап', sortable: true, width: '90px', visible: true },
  { key: 'status', label: 'Статус', sortable: true, width: '120px', visible: true },
  { key: 'year', label: 'Год', sortable: true, width: '70px', visible: true },

  // Учреждение
  {
    key: 'education_short_name',
    label: 'Учреждение',
    sortable: true,
    width: '200px',
    visible: true,
  },
  {
    key: 'education_institution_name',
    label: 'Полн. учреждение',
    sortable: true,
    width: '300px',
    visible: false,
  },

  // География
  {
    key: 'municipality_name',
    label: 'Муниципалитет',
    sortable: true,
    width: '180px',
    visible: true,
  },

  // Служебные
  { key: 'created_at', label: 'Создано', sortable: true, width: '160px', visible: false },
  { key: 'updated_at', label: 'Обновлено', sortable: true, width: '160px', visible: false },
]

const columnWidthMap = Object.fromEntries(columns.map((column) => [column.key, column.width]))
const getColumnWidth = (key, fallback = '160px') => columnWidthMap[key] || fallback

const stageOptions = computed(() =>
  olympiadsStore.filters.stages.map((s) => ({ label: s, value: s })),
)
const statusOptions = computed(() =>
  olympiadsStore.filters.statuses.map((s) => ({ label: s, value: s })),
)
const classOptions = computed(() =>
  olympiadsStore.filters.classes.map((c) => ({ label: String(c), value: c })),
)
const yearOptions = computed(() =>
  olympiadsStore.filters.years.map((y) => ({ label: String(y), value: y })),
)
const subjectOptions = computed(() =>
  olympiadsStore.filters.subjects.map((s) => ({ label: s.full_name, value: s.subject_id })),
)
const municipalityOptions = computed(() =>
  olympiadsStore.filters.municipalities.map((m) => ({ label: m.name, value: m.municipality_id })),
)
const educationOptions = computed(() => {
  let schools = olympiadsStore.filters.educations

  if (localMunicipalityFilter.value.length > 0) {
    schools = schools.filter((s) => localMunicipalityFilter.value.includes(s.municipality))
  }
  // Находим выбранные школы, которых нет в отфильтрованном списке и добавляем фразу "не в фильтре"
  const filteredIds = new Set(schools.map((s) => s.institution_id))
  const missingSelected = olympiadsStore.filters.educations
    .filter(
      (s) =>
        localEducationFilter.value.includes(s.institution_id) && !filteredIds.has(s.institution_id),
    )
    .map((s) => ({
      label: s.full_name + ' (другой муниципалитет)',
      value: s.institution_id,
      outOfFilter: true,
    }))

  return [
    ...missingSelected,
    ...schools.map((s) => ({ label: s.full_name, value: s.institution_id })),
  ]
})
const genderOptions = computed(() =>
  olympiadsStore.filters.genders.map((g) => ({ label: g, value: g })),
)

const tabs = [
  { value: 'manage', label: 'Управление' },
  { value: 'import', label: 'Импорт' },
  { value: 'export', label: 'Экспорт' },
]

const showEditDialog = ref(false)
const selectedParticipation = ref(null)
const showDeleteDialog = ref(false)

const openEditDialog = (row) => {
  selectedParticipation.value = row
  showEditDialog.value = true
}

const openDeleteDialog = (row) => {
  selectedParticipation.value = row
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedParticipation.value) return
  await olympiadsStore.deleteParticipation(selectedParticipation.value.olymp_id)
  showDeleteDialog.value = false
  selectedParticipation.value = null
}

const loadParticipations = () => {
  olympiadsStore.fetchParticipations()
}

const handleSort = ({ key, order }) => {
  olympiadsStore.ui.sortBy = key
  olympiadsStore.ui.sortOrder = order
  olympiadsStore.ui.page = 1
  loadParticipations()
}

const applyFilters = () => {
  olympiadsStore.ui.stageFilter = [...localStageFilter.value]
  olympiadsStore.ui.statusFilter = [...localStatusFilter.value]
  olympiadsStore.ui.classFilter = [...localClassFilter.value]
  olympiadsStore.ui.yearFilter = [...localYearFilter.value]
  olympiadsStore.ui.subjectFilter = [...localSubjectFilter.value]
  olympiadsStore.ui.municipalityFilter = [...localMunicipalityFilter.value]
  olympiadsStore.ui.educationFilter = [...localEducationFilter.value]
  olympiadsStore.ui.genderFilter = [...localGenderFilter.value]
  olympiadsStore.ui.page = 1
  loadParticipations()
}

const resetFilters = () => {
  localStageFilter.value = []
  localStatusFilter.value = []
  localClassFilter.value = []
  localYearFilter.value = []
  localSubjectFilter.value = []
  localMunicipalityFilter.value = []
  localEducationFilter.value = []
  localGenderFilter.value = []
  olympiadsStore.ui.stageFilter = []
  olympiadsStore.ui.statusFilter = []
  olympiadsStore.ui.classFilter = []
  olympiadsStore.ui.yearFilter = []
  olympiadsStore.ui.subjectFilter = []
  olympiadsStore.ui.municipalityFilter = []
  olympiadsStore.ui.educationFilter = []
  olympiadsStore.ui.genderFilter = []
  olympiadsStore.ui.search = ''
  olympiadsStore.ui.page = 1
  loadParticipations()
}

const changePageSize = (size) => {
  olympiadsStore.ui.pageSize = size
  olympiadsStore.ui.page = 1
  loadParticipations()
}

const getStageVariant = (stage) => {
  const map = {
    ШЭ: 'stage-she',
    МЭ: 'stage-me',
    РЭ: 'stage-re',
    ЗЭ: 'stage-ze',
  }
  return map[stage] || 'default'
}

const getStatusVariant = (status) => {
  const map = { победитель: 'primary', призёр: 'info', участник: 'success' }
  return map[status] || 'default'
}

onMounted(async () => {
  localStageFilter.value = [...olympiadsStore.ui.stageFilter]
  localStatusFilter.value = [...olympiadsStore.ui.statusFilter]
  localClassFilter.value = [...olympiadsStore.ui.classFilter]
  localYearFilter.value = [...olympiadsStore.ui.yearFilter]
  localSubjectFilter.value = [...olympiadsStore.ui.subjectFilter]
  localMunicipalityFilter.value = [...olympiadsStore.ui.municipalityFilter]
  localEducationFilter.value = [...olympiadsStore.ui.educationFilter]
  localGenderFilter.value = [...olympiadsStore.ui.genderFilter]

  await olympiadsStore.fetchFilters()
  await loadParticipations()
})
</script>

<template>
  <div class="olympiads-section">
    <BaseTabs v-model="olympiadsStore.ui.tab" :tabs="tabs" />

    <!-- Вкладка: Управление -->
    <div v-show="olympiadsStore.ui.tab === 'manage'" class="tab-content">
      <BaseCollapse
        v-model="olympiadsStore.ui.addFormOpen"
        title="Добавить участие в олимпиаде"
        open-title="Скрыть форму добавления"
      >
        <OlympiadsAddDialog />
      </BaseCollapse>
    </div>

    <!-- Вкладка: Импорт -->
    <div v-show="olympiadsStore.ui.tab === 'import'" class="tab-content">
      <ImportArea
        :open="olympiadsStore.ui.importOpen"
        @update:open="olympiadsStore.ui.importOpen = $event"
        :import-function="olympiadsStore.importParticipations"
        note-title="Требования к файлу:"
        @success="loadParticipations()"
      >
        <template #notes>
          <ul>
            <li>Поддерживаемые форматы: XLSX, CSV</li>
            <li style="line-height: 1.5">
              Обязательные поля: <strong>Фамилия</strong>, <strong>Имя</strong>,
              <strong>Пол</strong>, <strong>Дата рождения</strong>, <strong>Муниципалитет</strong>,
              <strong>ОУ</strong> / <strong>Полное наименование ОУ</strong>,
              <strong>Предмет</strong>, <strong>Класс</strong> / <strong>Класс обучения</strong>,
              <strong>Этап</strong>, <strong>Статус</strong> / <strong>Статус участника</strong>,
              <strong>Год</strong> / <strong>Год участия</strong>
            </li>
            <li>Необязательные поля: <strong>Отчество</strong></li>
            <li>Формат даты: ДД.ММ.ГГГГ или YYYY-MM-DD</li>
            <li>Пол: М, Ж, муж, жен, мужской, женский (с точкой или без, регистр не важен)</li>
            <li>Этап: ШЭ (школьный), МЭ (муниципальный), РЭ (региональный), ЗЭ (заключительный)</li>
            <li>Статус: победитель, призёр, участник</li>
            <li>Класс: целое число от 1 до 11</li>
            <li>Год: целое число от 1960 до {{ new Date().getFullYear() + 1 }}</li>
            <li style="line-height: 1.5">
              <strong>Важно:</strong> Муниципалитет, Учреждение и Предмет должны существовать в
              системе. Если они не найдены, импорт завершится с ошибкой для данной строки.
            </li>
          </ul>

          <span class="note-example-title">Примеры заголовков:</span>
          <CopyHeaders
            class="note-example"
            :variants="[
              {
                label: 'Вариант 1',
                headers: [
                  'Фамилия',
                  'Имя',
                  'Отчество',
                  'Пол',
                  'Дата рождения',
                  'Муниципалитет',
                  'ОУ',
                  'Предмет',
                  'Класс',
                  'Этап',
                  'Статус',
                  'Год',
                ],
                copyText:
                  'Фамилия, Имя, Отчество, Пол, Дата рождения, Муниципалитет, ОУ, Предмет, Класс, Этап, Статус, Год',
              },
              {
                label: 'Вариант 2',
                headers: [
                  'Фамилия',
                  'Имя',
                  'Отчество',
                  'Пол',
                  'Дата рождения',
                  'Муниципалитет',
                  'Полное наименование ОУ',
                  'Предмет',
                  'Класс обучения',
                  'Этап',
                  'Статус участника',
                  'Год участия',
                ],
                copyText:
                  'Фамилия, Имя, Отчество, Пол, Дата рождения, Муниципалитет, Полное наименование ОУ, Предмет, Класс обучения, Этап, Статус участника, Год участия',
              },
              {
                label: 'Вариант 3 (англ.)',
                headers: [
                  'participant_lastname',
                  'participant_firstname',
                  'participant_patronymic',
                  'participant_gender',
                  'participant_birth_date',
                  'municipality_name',
                  'education_institution_name',
                  'subject_full_name',
                  'class_field',
                  'stage',
                  'status',
                  'year',
                ],
                copyText:
                  'participant_lastname, participant_firstname, participant_patronymic, participant_gender, participant_birth_date, municipality_name, education_institution_name, subject_full_name, class_field, stage, status, year',
              },
            ]"
          />
          <p class="note-hint">
            Также принимаются: <strong>Полное наименование общеобразовательной организации</strong>,
            <strong>Полное название ОУ</strong>,
            <strong>Полное название общеобразовательной организации</strong>.
          </p>
        </template>
      </ImportArea>
    </div>

    <!-- Вкладка: Экспорт -->
    <div v-show="olympiadsStore.ui.tab === 'export'" class="tab-content">
      <ExportArea
        :open="olympiadsStore.ui.exportOpen"
        @update:open="olympiadsStore.ui.exportOpen = $event"
        :columns="[
          {
            title: 'Участник',
            columns: [
              { key: 'olymp_id', label: 'ID' },
              { key: 'participant_full_name', label: 'ФИО' },
              { key: 'participant_lastname', label: 'Фамилия' },
              { key: 'participant_firstname', label: 'Имя' },
              { key: 'participant_patronymic', label: 'Отчество' },
              { key: 'participant_birth_date', label: 'Дата рождения' },
              { key: 'participant_gender', label: 'Пол' },
            ],
          },
          {
            title: 'Образование',
            columns: [
              { key: 'municipality_name', label: 'Муниципалитет' },
              { key: 'education_institution_name', label: 'Учреждение' },
              { key: 'education_short_name', label: 'Крат. учреждение' },
              { key: 'subject_full_name', label: 'Предмет' },
              { key: 'subject_short_name', label: 'Крат. предмет' },
            ],
          },
          {
            title: 'Олимпиада',
            columns: [
              { key: 'class_field', label: 'Класс' },
              { key: 'stage', label: 'Этап' },
              { key: 'status', label: 'Статус' },
              { key: 'year', label: 'Год' },
            ],
          },
          {
            title: 'Системные',
            columns: [
              { key: 'created_at', label: 'Создано' },
              { key: 'updated_at', label: 'Обновлено' },
            ],
          },
        ]"
        :store="olympiadsStore"
        :export-function="olympiadsStore.exportParticipations"
        :show-filters-option="true"
      />
    </div>

    <!-- Поиск, фильтры, таблица -->
    <div class="common-section">
      <SearchBar
        v-model="olympiadsStore.ui.search"
        placeholder="Поиск по ФИО, учреждению, предмету"
        :timeout="500"
        @search="applyFilters"
        class="search-bar"
      />

      <FiltersPanel
        :extended="olympiadsStore.ui.filtersExtended"
        @update:extended="olympiadsStore.ui.filtersExtended = $event"
        :loading="olympiadsStore.isLoading"
        @apply="applyFilters"
        @reset="resetFilters"
      >
        <template #primary>
          <BaseMultiSelect
            v-model="localStageFilter"
            placeholder="Этап"
            :options="stageOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localStatusFilter"
            placeholder="Статус"
            :options="statusOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localYearFilter"
            placeholder="Год"
            :options="yearOptions"
            height="44px"
          />
          <BaseMultiSelect
            v-model="localSubjectFilter"
            placeholder="Предмет"
            :options="subjectOptions"
            height="44px"
          />
        </template>

        <template #extended>
          <BaseMultiSelect
            v-model="localMunicipalityFilter"
            placeholder="Муниципалитет"
            :options="municipalityOptions"
            height="44px"
            class="large"
          />
          <BaseMultiSelect
            v-model="localClassFilter"
            placeholder="Класс"
            :options="classOptions"
            height="44px"
            class="compact"
          />
          <BaseMultiSelect
            v-model="localGenderFilter"
            placeholder="Пол"
            :options="genderOptions"
            height="44px"
            class="compact"
          />
          <BaseMultiSelect
            v-model="localEducationFilter"
            placeholder="Учреждение"
            :options="educationOptions"
            height="44px"
            class="full"
          />
        </template>
      </FiltersPanel>

      <BaseTable
        :columns="columns"
        :data="olympiadsStore.participations"
        :visible-columns="olympiadsStore.ui.visibleColumns"
        :sort-by="olympiadsStore.ui.sortBy"
        :sort-order="olympiadsStore.ui.sortOrder"
        :loading="olympiadsStore.isLoading"
        :actions-column-width="'120px'"
        row-key="olymp_id"
        empty-message="Участия в олимпиаде не найдены"
        @sort="handleSort"
      >
        <template #cell-stage="{ value }">
          <BaseTag :label="value" :variant="getStageVariant(value)" size="small" />
        </template>

        <template #cell-status="{ value }">
          <BaseTag :label="value" :variant="getStatusVariant(value)" size="small" />
        </template>

        <template #cell-participant_birth_date="{ value }">
          <span v-if="value">
            {{ formatDate(value) }}
            <span class="age-badge">({{ calculateAge(value) }})</span>
          </span>
          <span v-else>—</span>
        </template>

        <template #cell-participant_gender="{ value }">
          <BaseTag :label="value" :variant="value === 'М' ? 'info' : 'error'" size="small" />
        </template>

        <template #cell-education_institution_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('education_institution_name')"
            max-height="90px"
          />
        </template>

        <template #cell-education_short_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('education_short_name')"
            max-height="50px"
          />
        </template>

        <template #cell-subject_full_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('subject_full_name')"
            max-height="60px"
          />
        </template>

        <template #cell-subject_short_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('subject_short_name')"
            max-height="60px"
          />
        </template>

        <template #cell-participant_full_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('participant_full_name')"
            nowrap
          />
        </template>

        <template #cell-municipality_name="{ value }">
          <BaseScrollableCell
            :text="value"
            :max-width="getColumnWidth('municipality_name')"
            max-height="60px"
          />
        </template>

        <template #cell-created_at="{ value }">
          {{ formatDateTime(value) }}
        </template>

        <template #cell-updated_at="{ value }">
          {{ formatDateTime(value) }}
        </template>

        <template #actions="{ row }">
          <div class="actions-cell">
            <BaseIconButton
              variant="ghost"
              size="medium"
              label="Редактировать"
              @click="openEditDialog(row)"
            >
              <EditIcon />
            </BaseIconButton>
            <BaseIconButton
              variant="danger"
              size="medium"
              label="Удалить"
              @click="openDeleteDialog(row)"
            >
              <TrashIcon />
            </BaseIconButton>
          </div>
        </template>

        <template #footer>
          <BaseColumnToggle
            :columns="columns"
            :model-value="olympiadsStore.ui.visibleColumns"
            @update:model-value="olympiadsStore.ui.visibleColumns = $event"
            position="top"
          />
          <BasePagination
            :model-value="olympiadsStore.ui.page"
            :total-items="olympiadsStore.total"
            :page-size="olympiadsStore.ui.pageSize"
            @update:page-size="changePageSize"
            @update:model-value="
              (page) => {
                olympiadsStore.ui.page = page
                loadParticipations()
              }
            "
          />
        </template>
      </BaseTable>
    </div>

    <OlympiadsEditDialog v-model="showEditDialog" :participation="selectedParticipation" />

    <DeleteDialog
      v-model="showDeleteDialog"
      entity-name="участие в олимпиаде"
      :item-name="`${selectedParticipation?.participant_full_name} (${selectedParticipation?.subject_full_name}, ${selectedParticipation?.year})`"
      :loading="olympiadsStore.isLoading"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.olympiads-section {
  width: 100%;
  background: var(--white);
  border-radius: 12px;
}

.tab-content {
  padding: 40px 40px 0;
}

.common-section {
  padding: 0 40px 40px;
}

.search-bar {
  margin-bottom: 24px;
}

.actions-cell {
  display: inline-flex;
  gap: 8px;
}

.age-badge {
  color: var(--text-tertiary);
  font-size: 12px;
  margin-left: 4px;
}

@media (max-width: 768px) {
  .tab-content {
    padding: 20px;
  }

  .common-section {
    padding: 0 20px 20px;
  }
}
</style>
