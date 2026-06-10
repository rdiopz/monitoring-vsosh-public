<script setup>
import { ref, onMounted } from 'vue'
import { useSubjectsStore } from '@entities/subjects'
import { useSectionState } from '@composables/useSectionState.js'

import ImportArea from '@/widgets/ImportArea/ImportArea.vue'
import ExportArea from '@/widgets/ExportArea/ExportArea.vue'
import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import CopyHeaders from '@/widgets/CopyHeaders/CopyHeaders.vue'

import BaseButton from '@ui/BaseButton.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseTabs from '@ui/BaseTabs.vue'
import BaseCollapse from '@ui/BaseCollapse.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import EmptyState from '@ui/EmptyState.vue'

import EditIcon from '@icons/actions/EditIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'
import SortAscIcon from '@icons/actions/SortAscIcon.vue'
import SortDescIcon from '@icons/actions/SortDescIcon.vue'

import SubjectsAddDialog from './components/SubjectsAddDialog.vue'
import SubjectsEditDialog from './components/SubjectsEditDialog.vue'

const subjectsStore = useSubjectsStore()

// Синхронизация ui с URL
useSectionState('subjects', subjectsStore)

const tabs = [
  { value: 'manage', label: 'Управление' },
  { value: 'import', label: 'Импорт' },
  { value: 'export', label: 'Экспорт' },
]

const showEditDialog = ref(false)
const selectedSubject = ref(null)

const openEditDialog = (subject) => {
  selectedSubject.value = subject
  showEditDialog.value = true
}

const showDeleteDialog = ref(false)

const openDeleteDialog = (subject) => {
  selectedSubject.value = subject
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedSubject.value) return
  await subjectsStore.deleteSubject(selectedSubject.value.subject_id)
  showDeleteDialog.value = false
  selectedSubject.value = null
}

onMounted(async () => {
  await subjectsStore.fetchSubjects()
})
</script>

<template>
  <div class="subjects-section">
    <BaseTabs v-model="subjectsStore.ui.tab" :tabs="tabs" />

    <!-- Вкладка: Управление -->
    <div v-show="subjectsStore.ui.tab === 'manage'" class="tab-content">
      <BaseCollapse
        v-model="subjectsStore.ui.addFormOpen"
        title="Добавить предмет"
        open-title="Скрыть форму добавления"
      >
        <SubjectsAddDialog />
      </BaseCollapse>
    </div>

    <!-- Вкладка: Импорт -->
    <div v-show="subjectsStore.ui.tab === 'import'" class="tab-content">
      <ImportArea
        :open="subjectsStore.ui.importOpen"
        @update:open="subjectsStore.ui.importOpen = $event"
        :import-function="subjectsStore.importSubjects"
        note-title="Требования к файлу:"
        @success="subjectsStore.fetchSubjects()"
      >
        <template #notes>
          <ul>
            <li>Поддерживаемые форматы: XLSX, CSV</li>
            <li>
              Обязательное поле: <strong>Полное название</strong> (или <strong>Предмет</strong>)
            </li>
            <li style="line-height: 1.5">
              Рекомендуется указывать поле: <strong>Краткое название</strong>.<br />
              Если оно не указано, сервер сгенерирует его автоматически — такое значение потребуется
              вручную отредактировать
            </li>
            <li>Максимальная длина полного названия: 100 символов</li>
            <li>Максимальная длина краткого названия: 25 символов</li>
          </ul>

          <span class="note-example-title">Пример заголовков:</span>
          <CopyHeaders
            class="note-example"
            :variants="[
              {
                label: 'Вариант 1',
                headers: ['Полное название', 'Краткое название'],
                copyText: 'Полное название, Краткое название',
              },
              {
                label: 'Вариант 2',
                headers: ['Предмет', 'Краткое название'],
                copyText: 'Предмет, Краткое название',
              },
              {
                label: 'Вариант 3',
                headers: ['full_name', 'short_name'],
                copyText: 'full_name, short_name',
              },
            ]"
          />
        </template>
      </ImportArea>
    </div>

    <!-- Вкладка: Экспорт -->
    <div v-show="subjectsStore.ui.tab === 'export'" class="tab-content">
      <ExportArea
        :open="subjectsStore.ui.exportOpen"
        @update:open="subjectsStore.ui.exportOpen = $event"
        :columns="[
          { key: 'subject_id', label: 'ID' },
          { key: 'full_name', label: 'Полное название' },
          { key: 'short_name', label: 'Краткое название' },
        ]"
        :store="subjectsStore"
        :export-function="subjectsStore.exportSubjects"
        :show-filters-option="false"
      />
    </div>

    <!-- Поиск и список -->
    <div class="common-section">
      <div class="toolbar">
        <SearchBar
          v-model="subjectsStore.ui.search"
          placeholder="Поиск по названию..."
          :timeout="500"
          @search="subjectsStore.fetchSubjects()"
        />
        <BaseButton
          @click="subjectsStore.toggleSort()"
          :title="subjectsStore.ui.sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'"
          :aria-label="subjectsStore.ui.sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'"
          variant="secondary"
          size="compact"
          label="Название"
        >
          <template #icon-left>
            <SortAscIcon v-if="subjectsStore.ui.sortOrder === 'asc'" />
            <SortDescIcon v-else />
          </template>
        </BaseButton>
      </div>

      <BaseSpinner v-if="subjectsStore.isLoading" text="Загрузка..." />

      <EmptyState v-else-if="subjectsStore.subjects.length === 0" message="Предметы не найдены" />

      <div v-else class="subjects-grid">
        <div
          v-for="subject in subjectsStore.subjects"
          :key="subject.subject_id"
          class="subject-card"
          :title="subject.full_name + (subject.short_name ? ' (' + subject.short_name + ')' : '')"
        >
          <span class="subject-id">#{{ subject.subject_id }}</span>

          <div class="subject-info">
            <span class="subject-name">{{ subject.full_name }}</span>
            <span v-if="subject.short_name" class="subject-short">{{ subject.short_name }}</span>
          </div>

          <div class="subject-actions">
            <BaseIconButton
              variant="ghost"
              size="medium"
              label="Редактировать"
              @click="openEditDialog(subject)"
            >
              <EditIcon />
            </BaseIconButton>
            <BaseIconButton
              variant="danger"
              size="medium"
              label="Удалить"
              @click="openDeleteDialog(subject)"
            >
              <TrashIcon />
            </BaseIconButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Диалоги -->
    <SubjectsEditDialog v-model="showEditDialog" :subject="selectedSubject" />

    <DeleteDialog
      v-model="showDeleteDialog"
      entity-name="предмет"
      :item-name="selectedSubject?.full_name ?? ''"
      :loading="subjectsStore.isLoading"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.subjects-section {
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

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.subject-card {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.2s ease;
  min-height: 120px;
  max-height: 140px;
  overflow: hidden;
}

.subject-card:hover {
  border-color: var(--secondary);
  box-shadow: 0 4px 12px rgba(67, 90, 170, 0.15);
  transform: translateY(-2px);
}

.subject-id {
  position: absolute;
  bottom: 8px;
  right: 28px;
  font-size: 12px;
  color: var(--text-tertiary);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.subject-card:hover .subject-id {
  opacity: 1;
}

.subject-info {
  flex: 1;
  min-width: 0;
  padding-right: 16px;
}

.subject-name {
  font: var(--medium-text);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.subject-short {
  font: var(--small-text);
  color: var(--text-tertiary);
  display: block;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-actions {
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

  .subjects-grid {
    grid-template-columns: 1fr;
  }

  .subject-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .subject-id {
    display: none;
  }

  .subject-actions {
    align-self: flex-end;
  }
}
</style>
