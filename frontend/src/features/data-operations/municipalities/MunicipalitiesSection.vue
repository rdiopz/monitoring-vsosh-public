<script setup>
import { ref, onMounted } from 'vue'
import { useMunicipalitiesStore } from '@entities/municipalities'
import { useSectionState } from '@composables/useSectionState.js'

import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import ExportArea from '@/widgets/ExportArea/ExportArea.vue'
import ImportArea from '@/widgets/ImportArea/ImportArea.vue'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import CopyHeaders from '@/widgets/CopyHeaders/CopyHeaders.vue'

import BaseButton from '@ui/BaseButton.vue'
import BaseCollapse from '@ui/BaseCollapse.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import BaseTabs from '@ui/BaseTabs.vue'
import EmptyState from '@ui/EmptyState.vue'

import EditIcon from '@icons/actions/EditIcon.vue'
import SortAscIcon from '@icons/actions/SortAscIcon.vue'
import SortDescIcon from '@icons/actions/SortDescIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'

import MunicipalitiesAddDialog from './components/MunicipalitiesAddDialog.vue'
import MunicipalitiesEditDialog from './components/MunicipalitiesEditDialog.vue'

const municipalitiesStore = useMunicipalitiesStore()

// Синхронизация ui с URL
useSectionState('municipalities', municipalitiesStore)

const tabs = [
  { value: 'manage', label: 'Управление' },
  { value: 'import', label: 'Импорт' },
  { value: 'export', label: 'Экспорт' },
]

const showEditDialog = ref(false)
const selectedMunicipality = ref(null)

const openEditDialog = (municipality) => {
  selectedMunicipality.value = municipality
  showEditDialog.value = true
}

const showDeleteDialog = ref(false)

const openDeleteDialog = (municipality) => {
  selectedMunicipality.value = municipality
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedMunicipality.value) return
  await municipalitiesStore.deleteMunicipality(selectedMunicipality.value.municipality_id)
  showDeleteDialog.value = false
  selectedMunicipality.value = null
}

onMounted(async () => {
  await municipalitiesStore.fetchMunicipalities()
})
</script>

<template>
  <div class="municipalities-section">
    <BaseTabs v-model="municipalitiesStore.ui.tab" :tabs="tabs" />

    <!-- Вкладка: Управление -->
    <div v-show="municipalitiesStore.ui.tab === 'manage'" class="tab-content">
      <BaseCollapse
        v-model="municipalitiesStore.ui.addFormOpen"
        title="Добавить муниципалитет"
        open-title="Скрыть форму добавления"
      >
        <MunicipalitiesAddDialog />
      </BaseCollapse>
    </div>

    <!-- Вкладка: Импорт -->
    <div v-show="municipalitiesStore.ui.tab === 'import'" class="tab-content">
      <ImportArea
        :open="municipalitiesStore.ui.importOpen"
        @update:open="municipalitiesStore.ui.importOpen = $event"
        :import-function="municipalitiesStore.importMunicipalities"
        note-title="Требования к файлу:"
        @success="municipalitiesStore.fetchMunicipalities()"
      >
        <template #notes>
          <ul>
            <li>Поддерживаемые форматы: XLSX, CSV</li>
            <li>
              Обязательное поле: <strong>Название</strong> (или <strong>Муниципалитет</strong>)
            </li>
            <li>Максимальная длина названия: 150 символов</li>
          </ul>

          <span class="note-example-title">Пример заголовков:</span>
          <CopyHeaders
            class="note-example"
            :variants="[
              {
                label: 'Вариант 1',
                headers: ['Название'],
                copyText: 'Название',
              },
              {
                label: 'Вариант 2',
                headers: ['Муниципалитет'],
                copyText: 'Муниципалитет',
              },
              {
                label: 'Вариант 3',
                headers: ['name'],
                copyText: 'name',
              },
            ]"
          />
        </template>
      </ImportArea>
    </div>

    <!-- Вкладка: Экспорт -->
    <div v-show="municipalitiesStore.ui.tab === 'export'" class="tab-content">
      <ExportArea
        :open="municipalitiesStore.ui.exportOpen"
        @update:open="municipalitiesStore.ui.exportOpen = $event"
        :columns="[
          { key: 'municipality_id', label: 'ID' },
          { key: 'name', label: 'Название' },
        ]"
        :store="municipalitiesStore"
        :export-function="municipalitiesStore.exportMunicipalities"
        :show-filters-option="false"
      />
    </div>

    <!-- Поиск и список -->
    <div class="common-section">
      <div class="toolbar">
        <SearchBar
          v-model="municipalitiesStore.ui.search"
          placeholder="Поиск по названию..."
          :timeout="500"
          @search="municipalitiesStore.fetchMunicipalities()"
        />
        <BaseButton
          @click="municipalitiesStore.toggleSort()"
          :title="municipalitiesStore.ui.sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'"
          :aria-label="
            municipalitiesStore.ui.sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'
          "
          variant="secondary"
          size="compact"
          label="Название"
        >
          <template #icon-left>
            <SortAscIcon v-if="municipalitiesStore.ui.sortOrder === 'asc'" />
            <SortDescIcon v-else />
          </template>
        </BaseButton>
      </div>

      <BaseSpinner v-if="municipalitiesStore.isLoading" text="Загрузка..." />

      <EmptyState
        v-else-if="municipalitiesStore.municipalities.length === 0"
        message="Муниципалитеты не найдены"
      />

      <div v-else class="municipalities-grid">
        <div
          v-for="municipality in municipalitiesStore.municipalities"
          :key="municipality.municipality_id"
          class="municipality-card"
          :title="municipality.name"
        >
          <span class="municipality-id">#{{ municipality.municipality_id }}</span>

          <div class="municipality-info">
            <span class="municipality-name">{{ municipality.name }}</span>
          </div>

          <div class="municipality-actions">
            <BaseIconButton
              variant="ghost"
              size="medium"
              label="Редактировать"
              @click="openEditDialog(municipality)"
            >
              <EditIcon />
            </BaseIconButton>
            <BaseIconButton
              variant="danger"
              size="medium"
              label="Удалить"
              @click="openDeleteDialog(municipality)"
            >
              <TrashIcon />
            </BaseIconButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Диалоги -->
    <MunicipalitiesEditDialog v-model="showEditDialog" :municipality="selectedMunicipality" />

    <DeleteDialog
      v-model="showDeleteDialog"
      entity-name="муниципалитет"
      :item-name="selectedMunicipality?.name ?? ''"
      :loading="municipalitiesStore.isLoading"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.municipalities-section {
  width: 100%;
  background: var(--white);
  border-radius: 12px;
  overflow: hidden;
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
  margin-bottom: 30px;
}

.municipalities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.municipality-card {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.2s ease;
  min-height: 80px;
  max-height: 100px;
  overflow: hidden;
}

.municipality-card:hover {
  border-color: var(--secondary);
  box-shadow: 0 4px 12px rgba(67, 90, 170, 0.15);
  transform: translateY(-2px);
}

.municipality-id {
  position: absolute;
  bottom: 2px;
  right: 28px;
  font-size: 12px;
  color: var(--text-tertiary);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.municipality-card:hover .municipality-id {
  opacity: 1;
}

.municipality-info {
  flex: 1;
  min-width: 0;
  padding-right: 16px;
}

.municipality-name {
  font: var(--medium-text);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.municipality-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .tab-content {
    padding: 20px;
  }

  .common-section {
    padding: 0 20px 20px;
  }

  .municipalities-grid {
    grid-template-columns: 1fr;
  }

  .municipality-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .municipality-id {
    display: none;
  }

  .municipality-actions {
    align-self: flex-end;
  }
}
</style>
