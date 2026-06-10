<script setup>
import { ref, onMounted } from 'vue'
import { useParticipantsStore } from '@entities/participants'
import { useSectionState } from '@composables/useSectionState.js'
import { formatDate, calculateAge } from '@utils/date'

import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import ExportArea from '@/widgets/ExportArea/ExportArea.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'
import ImportArea from '@/widgets/ImportArea/ImportArea.vue'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import CopyHeaders from '@/widgets/CopyHeaders/CopyHeaders.vue'

import BaseCollapse from '@ui/BaseCollapse.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseTable from '@ui/BaseTable.vue'
import BaseColumnToggle from '@ui/BaseColumnToggle.vue'
import BasePagination from '@ui/BasePagination.vue'
import BaseTabs from '@ui/BaseTabs.vue'
import BaseTag from '@ui/BaseTag.vue'

import EditIcon from '@icons/actions/EditIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'

import ParticipantsAddDialog from './components/ParticipantsAddDialog.vue'
import ParticipantsEditDialog from './components/ParticipantsEditDialog.vue'

const participantsStore = useParticipantsStore()

useSectionState('participants', participantsStore)

const localGenderFilter = ref([])
const localDateFrom = ref(null)
const localDateTo = ref(null)
const localSearch = ref('')

const columns = [
  { key: 'participant_id', label: 'ID', sortable: true, width: '80px' },
  { key: 'lastname', label: 'Фамилия', sortable: true, width: '160px', visible: false },
  { key: 'firstname', label: 'Имя', sortable: true, width: '160px', visible: false },
  { key: 'patronymic', label: 'Отчество', sortable: true, width: '160px', visible: false },
  { key: 'full_name', label: 'ФИО', sortable: true },
  { key: 'gender', label: 'Пол', sortable: true, width: '80px' },
  { key: 'birth_date', label: 'Дата рождения', sortable: true },
]

const genderOptions = [
  { label: 'М', value: 'М' },
  { label: 'Ж', value: 'Ж' },
]

const tabs = [
  { value: 'manage', label: 'Управление' },
  { value: 'import', label: 'Импорт' },
  { value: 'export', label: 'Экспорт' },
]

const showEditDialog = ref(false)
const selectedParticipant = ref(null)

const openEditDialog = (participant) => {
  selectedParticipant.value = participant
  showEditDialog.value = true
}

const showDeleteDialog = ref(false)

const openDeleteDialog = (participant) => {
  selectedParticipant.value = participant
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedParticipant.value) return
  await participantsStore.deleteParticipant(selectedParticipant.value.participant_id)
  showDeleteDialog.value = false
  selectedParticipant.value = null
}

const loadParticipants = () => {
  participantsStore.fetchParticipants()
}

const handleSort = ({ key, order }) => {
  participantsStore.ui.sortBy = key
  participantsStore.ui.sortOrder = order
  participantsStore.ui.page = 1
  loadParticipants()
}

// Преобразование даты во время поиска
const normalizeParticipantSearch = (value) => {
  if (!value) return ''

  return value
    .replace(
      /\b(\d{2})[./-](\d{2})[./-](\d{4})\b/g,
      (_, day, month, year) => `${day} ${month} ${year}`,
    )
    .replace(/\s+/g, ' ')
    .trim()
}

const applyFilters = () => {
  participantsStore.ui.search = normalizeParticipantSearch(localSearch.value)
  participantsStore.ui.genderFilter = [...localGenderFilter.value]
  participantsStore.ui.dateFrom = localDateFrom.value
  participantsStore.ui.dateTo = localDateTo.value
  participantsStore.ui.page = 1
  loadParticipants()
}

const resetFilters = () => {
  localSearch.value = ''
  localGenderFilter.value = []
  localDateFrom.value = null
  localDateTo.value = null
  participantsStore.ui.genderFilter = []
  participantsStore.ui.dateFrom = null
  participantsStore.ui.dateTo = null
  participantsStore.ui.search = ''
  participantsStore.ui.page = 1
  loadParticipants()
}

const changePageSize = (size) => {
  participantsStore.ui.pageSize = size
  participantsStore.ui.page = 1
  loadParticipants()
}

onMounted(async () => {
  localGenderFilter.value = [...participantsStore.ui.genderFilter]
  localDateFrom.value = participantsStore.ui.dateFrom
  localDateTo.value = participantsStore.ui.dateTo

  await loadParticipants()
})
</script>

<template>
  <div class="participants-section">
    <BaseTabs v-model="participantsStore.ui.tab" :tabs="tabs" />

    <!-- Управление -->
    <div v-show="participantsStore.ui.tab === 'manage'" class="tab-content">
      <BaseCollapse
        v-model="participantsStore.ui.addFormOpen"
        title="Добавить участника"
        open-title="Скрыть форму добавления"
      >
        <ParticipantsAddDialog />
      </BaseCollapse>
    </div>

    <!-- Импорт -->
    <div v-show="participantsStore.ui.tab === 'import'" class="tab-content">
      <ImportArea
        :open="participantsStore.ui.importOpen"
        @update:open="participantsStore.ui.importOpen = $event"
        :import-function="participantsStore.importParticipants"
        note-title="Требования к файлу:"
        @success="loadParticipants()"
      >
        <template #notes>
          <ul>
            <li>Поддерживаемые форматы: XLSX, CSV</li>
            <li>
              Обязательные поля: <strong>Фамилия</strong>, <strong>Имя</strong>,
              <strong>Пол</strong>, <strong>Дата рождения</strong>
            </li>
            <li>Максимальная длина: Фамилия/Имя/Отчество — 150 символов</li>
            <li>Формат даты: ДД.ММ.ГГГГ или YYYY-MM-DD</li>
            <li>Пол: М, Ж, муж, жен, мужской, женский (с точкой или без, регистр не важен)</li>
          </ul>

          <span class="note-example-title">Пример заголовков:</span>
          <CopyHeaders
            class="note-example"
            :variants="[
              {
                label: 'Вариант 1',
                headers: ['Фамилия', 'Имя', 'Отчество', 'Пол', 'Дата рождения'],
                copyText: 'Фамилия, Имя, Отчество, Пол, Дата рождения',
              },
              {
                label: 'Вариант 2',
                headers: ['lastname', 'firstname', 'patronymic', 'gender', 'birth_date'],
                copyText: 'lastname, firstname, patronymic, gender, birth_date',
              },
            ]"
          />
        </template>
      </ImportArea>
    </div>

    <!-- Экспорт -->
    <div v-show="participantsStore.ui.tab === 'export'" class="tab-content">
      <ExportArea
        :open="participantsStore.ui.exportOpen"
        @update:open="participantsStore.ui.exportOpen = $event"
        :columns="[
          { key: 'participant_id', label: 'ID' },
          { key: 'lastname', label: 'Фамилия' },
          { key: 'firstname', label: 'Имя' },
          { key: 'patronymic', label: 'Отчество' },
          { key: 'full_name', label: 'ФИО' },
          { key: 'birth_date', label: 'Дата рождения' },
          { key: 'gender', label: 'Пол' },
        ]"
        :store="participantsStore"
        :export-function="participantsStore.exportParticipants"
        :show-filters-option="true"
      />
    </div>

    <!-- Поиск, фильтры, таблица -->
    <div class="common-section">
      <SearchBar
        v-model="localSearch"
        placeholder="Поиск по ФИО, дате рождения"
        :timeout="500"
        @search="applyFilters"
        class="search-bar"
      />

      <FiltersPanel
        :extended="participantsStore.ui.filtersExtended"
        @update:extended="participantsStore.ui.filtersExtended = $event"
        :loading="participantsStore.isLoading"
        @apply="applyFilters"
        @reset="resetFilters"
      >
        <template #primary>
          <BaseMultiSelect
            v-model="localGenderFilter"
            placeholder="Пол"
            :options="genderOptions"
            height="44px"
            class="medium"
          />
        </template>

        <template #extended>
          <BaseDatePicker
            v-model="localDateFrom"
            mode="single"
            :enable-time="false"
            date-format="d.m.Y"
            placeholder="Дата рождения с"
            height="44px"
            class="medium"
            :clearable="true"
          />
          <BaseDatePicker
            v-model="localDateTo"
            mode="single"
            :enable-time="false"
            date-format="d.m.Y"
            placeholder="Дата рождения по"
            height="44px"
            class="medium"
            :clearable="true"
          />
        </template>
      </FiltersPanel>

      <BaseTable
        :columns="columns"
        :data="participantsStore.participants"
        :visible-columns="participantsStore.ui.visibleColumns"
        :sort-by="participantsStore.ui.sortBy"
        :sort-order="participantsStore.ui.sortOrder"
        :loading="participantsStore.isLoading"
        :actions-column-width="'120px'"
        row-key="participant_id"
        empty-message="Участники не найдены"
        @sort="handleSort"
      >
        <template #cell-gender="{ value }">
          <BaseTag :label="value" :variant="value === 'М' ? 'info' : 'error'" size="small" />
        </template>

        <template #cell-birth_date="{ value }">
          <span v-if="value">
            {{ formatDate(value) }}
            <span class="age-badge">({{ calculateAge(value) }})</span>
          </span>
          <span v-else>—</span>
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
            :model-value="participantsStore.ui.visibleColumns"
            @update:model-value="participantsStore.ui.visibleColumns = $event"
            position="top"
          />
          <BasePagination
            :model-value="participantsStore.ui.page"
            :total-items="participantsStore.total"
            :page-size="participantsStore.ui.pageSize"
            @update:page-size="changePageSize"
            @update:model-value="
              (page) => {
                participantsStore.ui.page = page
                loadParticipants()
              }
            "
          />
        </template>
      </BaseTable>
    </div>

    <ParticipantsEditDialog v-model="showEditDialog" :participant="selectedParticipant" />

    <DeleteDialog
      v-model="showDeleteDialog"
      entity-name="участника"
      :item-name="selectedParticipant?.full_name ?? ''"
      :loading="participantsStore.isLoading"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.participants-section {
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
