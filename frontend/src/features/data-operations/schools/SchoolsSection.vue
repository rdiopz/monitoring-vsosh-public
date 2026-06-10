<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSchoolsStore } from '@entities/schools'
import { useSectionState } from '@composables/useSectionState.js'

import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import ExportArea from '@/widgets/ExportArea/ExportArea.vue'
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

import EditIcon from '@icons/actions/EditIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'

import SchoolsAddDialog from './components/SchoolsAddDialog.vue'
import SchoolsEditDialog from './components/SchoolsEditDialog.vue'
import BaseScrollableCell from '@/shared/ui/BaseScrollableCell.vue'

const schoolsStore = useSchoolsStore()

// Синхронизация ui с URL
useSectionState('schools', schoolsStore)

const columns = [
  { key: 'institution_id', label: 'ID', sortable: true, width: '80px' },
  { key: 'municipality_name', label: 'Муниципалитет', sortable: true, width: '200px' },
  { key: 'short_name', label: 'Краткое наименование', sortable: true },
  { key: 'full_name', label: 'Полное наименование', sortable: true },
]

const municipalityOptions = computed(() => {
  return schoolsStore.filters.municipalities.map((m) => ({
    label: m.name,
    value: m.municipality_id,
  }))
})

const tabs = [
  { value: 'manage', label: 'Управление' },
  { value: 'import', label: 'Импорт' },
  { value: 'export', label: 'Экспорт' },
]

const showEditDialog = ref(false)
const selectedSchool = ref(null)

const openEditDialog = (school) => {
  selectedSchool.value = school
  showEditDialog.value = true
}

const showDeleteDialog = ref(false)

const openDeleteDialog = (school) => {
  selectedSchool.value = school
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedSchool.value) return
  await schoolsStore.deleteSchool(selectedSchool.value.institution_id)
  showDeleteDialog.value = false
  selectedSchool.value = null
}

const loadSchools = () => {
  schoolsStore.fetchSchools()
}

const handleSort = ({ key, order }) => {
  schoolsStore.ui.sortBy = key
  schoolsStore.ui.sortOrder = order
  schoolsStore.ui.page = 1
  loadSchools()
}

const onFilterChange = () => {
  schoolsStore.ui.page = 1
  loadSchools()
}

const changePageSize = (size) => {
  schoolsStore.ui.pageSize = size
  schoolsStore.ui.page = 1
  loadSchools()
}

onMounted(async () => {
  await schoolsStore.fetchFilters()
  await loadSchools()
})
</script>

<template>
  <div class="schools-section">
    <BaseTabs v-model="schoolsStore.ui.tab" :tabs="tabs" />

    <!-- Вкладка: Управление -->
    <div v-show="schoolsStore.ui.tab === 'manage'" class="tab-content">
      <BaseCollapse
        v-model="schoolsStore.ui.addFormOpen"
        title="Добавить учреждение"
        open-title="Скрыть форму добавления"
      >
        <SchoolsAddDialog />
      </BaseCollapse>
    </div>

    <!-- Вкладка: Импорт -->
    <div v-show="schoolsStore.ui.tab === 'import'" class="tab-content">
      <ImportArea
        :open="schoolsStore.ui.importOpen"
        @update:open="schoolsStore.ui.importOpen = $event"
        :import-function="schoolsStore.importSchools"
        note-title="Требования к файлу:"
        @success="loadSchools()"
      >
        <template #notes>
          <ul>
            <li>Поддерживаемые форматы: XLSX, CSV</li>
            <li>
              Обязательные поля: <strong>Муниципалитет</strong>, <strong>ОУ</strong> /
              <strong>Полное наименование ОУ</strong>
            </li>
            <li style="line-height: 1.5">
              Рекомендуется указывать поле: <strong>Краткое наименование</strong> /
              <strong>Краткое название</strong>.<br />
              Если оно не указано, сервер сгенерирует его автоматически — такое значение потребуется
              вручную отредактировать
            </li>
            <li>Максимальная длина: Полное наименование — 500 символов, Краткое — 300 символов</li>
          </ul>

          <span class="note-example-title">Примеры заголовков:</span>
          <CopyHeaders
            class="note-example"
            :variants="[
              {
                label: 'Вариант 1',
                headers: ['Муниципалитет', 'Полное наименование ОУ', 'Краткое наименование ОУ'],
                copyText: 'Муниципалитет, Полное наименование ОУ, Краткое наименование ОУ',
              },
              {
                label: 'Вариант 2',
                headers: ['Муниципалитет', 'ОУ', 'Краткое название ОУ'],
                copyText: 'Муниципалитет, ОУ, Краткое название ОУ',
              },
              {
                label: 'Вариант 3',
                headers: ['municipality_name', 'full_name', 'short_name'],
                copyText: 'municipality_name, full_name, short_name',
              },
            ]"
          />
          <p class="note-hint">
            Также принимаются: <strong>Полное наименование общеобразовательной организации</strong>,
            <strong>Полное название общеобразовательной организации</strong>,
            <strong>Полное название ОУ</strong>.
          </p>
        </template>
      </ImportArea>
    </div>

    <!-- Вкладка: Экспорт -->
    <div v-show="schoolsStore.ui.tab === 'export'" class="tab-content">
      <ExportArea
        :open="schoolsStore.ui.exportOpen"
        @update:open="schoolsStore.ui.exportOpen = $event"
        :columns="[
          { key: 'institution_id', label: 'ID' },
          { key: 'municipality_name', label: 'Муниципалитет' },
          { key: 'full_name', label: 'Полное наименование' },
          { key: 'short_name', label: 'Краткое наименование' },
        ]"
        :store="schoolsStore"
        :export-function="schoolsStore.exportSchools"
        :show-filters-option="true"
      />
    </div>

    <!-- Поиск, фильтры, таблица -->
    <div class="common-section">
      <div class="toolbar">
        <SearchBar
          v-model="schoolsStore.ui.search"
          placeholder="Поиск по наименованию"
          :timeout="500"
          @search="onFilterChange"
        />
        <BaseMultiSelect
          v-model="schoolsStore.ui.municipalityFilter"
          placeholder="Муниципалитет"
          :options="municipalityOptions"
          height="50px"
          width="100%"
          class="toolbar-filter"
          @update:model-value="onFilterChange"
        />
      </div>

      <BaseTable
        :columns="columns"
        :data="schoolsStore.schools"
        :visible-columns="schoolsStore.ui.visibleColumns"
        :sort-by="schoolsStore.ui.sortBy"
        :sort-order="schoolsStore.ui.sortOrder"
        :loading="schoolsStore.isLoading"
        :actions-column-width="'100px'"
        row-key="institution_id"
        empty-message="Образовательные учреждения не найдены"
        @sort="handleSort"
      >
        <template #cell-full_name="{ value }">
          <BaseScrollableCell :text="value" max-height="60px" max-width="100%" />
        </template>

        <template #cell-short_name="{ value }">
          <BaseScrollableCell :text="value" max-height="60px" max-width="100%" />
        </template>

        <template #cell-municipality_name="{ value }">
          <BaseScrollableCell :text="value" max-height="60px" max-width="100%" />
        </template>

        <template #actions="{ row }">
          <div class="action-cell">
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
            :model-value="schoolsStore.ui.visibleColumns"
            @update:model-value="schoolsStore.ui.visibleColumns = $event"
            position="top"
          />
          <BasePagination
            :model-value="schoolsStore.ui.page"
            :total-items="schoolsStore.total"
            :page-size="schoolsStore.ui.pageSize"
            @update:page-size="changePageSize"
            @update:model-value="
              (page) => {
                schoolsStore.ui.page = page
                loadSchools()
              }
            "
          />
        </template>
      </BaseTable>
    </div>

    <SchoolsEditDialog v-model="showEditDialog" :school="selectedSchool" />

    <DeleteDialog
      v-model="showDeleteDialog"
      entity-name="учреждение"
      :item-name="selectedSchool?.full_name ?? ''"
      :loading="schoolsStore.isLoading"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.schools-section {
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

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}

.toolbar-filter {
  width: 25%;
  flex-shrink: 0;
}

.action-cell {
  display: inline-flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .tab-content {
    padding: 20px;
  }

  .common-section {
    padding: 0 20px 20px;
  }

  .toolbar {
    flex-wrap: wrap;
  }

  .toolbar-filter {
    width: 100%;
  }
}
</style>
