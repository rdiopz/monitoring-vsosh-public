<script setup>
import FileIcon from '@icons/actions/FileIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import BaseButton from '@ui/BaseButton.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import BaseCollapse from '@ui/BaseCollapse.vue'
import { useImport } from './useImport'

const props = defineProps({
  importFunction: {
    type: Function,
    required: true,
  },
  noteTitle: {
    type: String,
    default: 'Требования к файлу:',
  },
  open: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['success', 'update:open'])

const {
  importResponse,
  isDragOver,
  isImporting,
  fileInputRef,
  handleFileSelect,
  triggerFileInput,
  handleDragOver,
  handleDragLeave,
  handleDrop,
  cleanErrorMessage,
  clearImportResponse,
} = useImport(props.importFunction, () => emit('success'))
</script>

<template>
  <BaseCollapse
    :model-value="open"
    title="Импорт данных"
    open-title="Скрыть область импорта"
    @update:model-value="emit('update:open', $event)"
  >
    <div
      class="drop-zone"
      :class="{ 'drop-zone--dragover': isDragOver, 'drop-zone--importing': isImporting }"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <template v-if="isImporting">
        <BaseSpinner size="48px" text="Обработка файла..." />
      </template>
      <template v-else>
        <span class="drop-zone-text">Перетащите файл сюда (XLSX, CSV)</span>
        <span class="drop-zone-or">или</span>
        <input
          ref="fileInputRef"
          type="file"
          accept=".xlsx,.csv"
          class="file-input"
          @change="handleFileSelect"
        />
        <BaseButton variant="primary" size="medium" @click="triggerFileInput">
          <template #icon-left>
            <FileIcon />
          </template>
          Выберите файл
        </BaseButton>
      </template>
    </div>

    <div class="import-note">
      <span class="import-note-title">{{ noteTitle }}</span>
      <div class="import-note-content">
        <slot name="notes" />
      </div>
    </div>

    <!-- Ошибки импорта -->
    <div v-if="importResponse && importResponse.errors > 0" class="import-errors">
      <div class="import-errors-header">
        <span class="import-errors-title">Ошибки импорта ({{ importResponse.errors }})</span>
        <BaseIconButton
          variant="ghost"
          borderless
          size="small"
          label="Скрыть ошибки импорта"
          @click="clearImportResponse"
        >
          <ClearIcon />
        </BaseIconButton>
      </div>
      <ul class="import-errors-list">
        <li
          v-for="(errorDetail, index) in importResponse.error_details"
          :key="index"
          class="import-error-item"
        >
          <span class="error-row-badge">Строка {{ errorDetail.row }}</span>
          <span class="error-message">{{ cleanErrorMessage(errorDetail.error) }}</span>
        </li>
      </ul>
    </div>

    <!-- Успешный импорт -->
    <div
      v-if="importResponse && importResponse.errors === undefined && importResponse.message"
      class="import-success"
    >
      <span class="success-summary">
        Создано: {{ importResponse.created }}, Обновлено: {{ importResponse.updated }}
      </span>
      <BaseIconButton
        variant="ghost"
        borderless
        size="small"
        label="Скрыть результат импорта"
        @click="clearImportResponse"
      >
        <ClearIcon />
      </BaseIconButton>
    </div>
  </BaseCollapse>
</template>

<style scoped>
.drop-zone {
  border: 2px dashed var(--secondary);
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  transition: all 0.3s ease;
  background: var(--white);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.drop-zone--dragover {
  border-color: var(--secondary);
  background: color-mix(in srgb, var(--secondary) 5%, transparent);
}

.drop-zone--importing {
  border-color: var(--info);
  background: color-mix(in srgb, var(--info) 5%, transparent);
  pointer-events: none;
}

.drop-zone-text {
  font: var(--medium-text);
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.drop-zone-or {
  font: var(--small-text);
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.file-input {
  display: none;
}

.import-note {
  margin-top: 24px;
  padding: 20px;
  background: var(--white);
  border-radius: 8px;
  border-left: 4px solid var(--secondary);
}

.import-note-title {
  display: block;
  font: var(--medium-text);
  color: var(--text-primary);
  margin-bottom: 12px;
}

.import-note-content :deep(ul) {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);
  font: var(--small-text);
}

.import-note-content :deep(li) {
  margin-bottom: 8px;
}

.import-note-content :deep(.note-hint) {
  margin-top: 8px;
  font: var(--tiny-text);
  color: var(--text-tertiary);
  line-height: 1.5;
}

.import-errors {
  margin-top: 24px;
  border: 1px solid color-mix(in srgb, var(--error) 30%, transparent);
  border-radius: 12px;
  overflow: hidden;
  background: var(--white);
}

.import-errors-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: color-mix(in srgb, var(--error) 8%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--error) 20%, transparent);
}

.import-errors-title {
  font: var(--medium-text);
  color: var(--error);
}

.import-errors-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 400px;
  overflow-y: auto;
}

.import-error-item {
  display: flex;
  gap: 16px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--color-border);
}

.import-error-item:last-child {
  border-bottom: none;
}

.import-note-content :deep(.note-example-title) {
  display: block;
  font: var(--medium-text);
  color: var(--text-primary);
  margin: 16px 0 12px;
}

.error-row-badge {
  flex-shrink: 0;
  min-width: 80px;
  font: var(--semibold-head-text);
  color: var(--text-secondary);
  background: var(--color-background-soft);
  padding: 4px 10px;
  border-radius: 4px;
  text-align: center;
}

.error-message {
  flex: 1;
  font: var(--small-text);
  color: var(--error);
  word-break: break-word;
  line-height: 1.5;
}

.import-success {
  margin-top: 24px;
  padding: 20px 24px;
  border: 1px solid color-mix(in srgb, var(--success) 30%, transparent);
  border-radius: 12px;
  background: color-mix(in srgb, var(--success) 5%, transparent);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.success-summary {
  flex: 1;
  text-align: center;
  font: var(--small-text);
  color: var(--text-secondary);
}
</style>
