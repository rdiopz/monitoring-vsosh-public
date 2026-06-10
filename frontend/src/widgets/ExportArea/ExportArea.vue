<script setup>
import { computed } from 'vue'
import BaseButton from '@ui/BaseButton.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import BaseCollapse from '@ui/BaseCollapse.vue'
import ExportIcon from '@icons/actions/ExportIcon.vue'
import { useExport } from './useExport'

const props = defineProps({
  store: {
    type: Object,
    required: true,
  },
  exportFunction: {
    type: Function,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  open: {
    type: Boolean,
    default: true,
  },
  showFiltersOption: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:open'])

const {
  exportWithFilters,
  exportError,
  selectedExportColumns,
  setColumnsOrder,
  toggleColumn,
  toggleAll,
  resetToDefault,
  handleExport,
} = useExport(props.store, props.exportFunction)

const selected = computed(() => selectedExportColumns.value)

const isGrouped = computed(() => {
  return props.columns.length > 0 && 'columns' in props.columns[0]
})

const flatColumns = computed(() => {
  if (isGrouped.value) {
    return props.columns.flatMap((group) => group.columns)
  }
  return props.columns
})

const allKeys = computed(() => {
  return flatColumns.value.map((col) => col.key)
})

const filtersLabel = computed(() => {
  if (props.showFiltersOption) {
    return 'Экспортировать с учётом текущих параметров (поиск, сортировка, фильтры)'
  }
  return 'Экспортировать с учётом текущих параметров (поиск, сортировка)'
})

const isChecked = (key) => {
  return selected.value.includes(key)
}

setColumnsOrder(allKeys.value)
</script>

<template>
  <BaseCollapse
    :model-value="open"
    title="Настройки экспорта"
    open-title="Скрыть настройки экспорта"
    @update:model-value="emit('update:open', $event)"
  >
    <div class="export-body">
      <div class="export-columns">
        <span class="export-subtitle">Колонки для экспорта:</span>

        <template v-if="isGrouped">
          <div v-for="group in columns" :key="group.title" class="export-group">
            <span class="export-group-title">{{ group.title }}</span>
            <div class="columns-grid">
              <div v-for="col in group.columns" :key="col.key" class="column-item">
                <BaseCheckBox
                  :model-value="isChecked(col.key)"
                  @update:model-value="toggleColumn(col.key)"
                >
                  {{ col.label }}
                </BaseCheckBox>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="columns-grid">
            <div v-for="col in columns" :key="col.key" class="column-item">
              <BaseCheckBox
                :model-value="isChecked(col.key)"
                @update:model-value="toggleColumn(col.key)"
              >
                {{ col.label }}
              </BaseCheckBox>
            </div>
          </div>
        </template>

        <div class="export-columns-actions">
          <button class="export-action-btn" @click="toggleAll(allKeys)">
            {{ selected.length === allKeys.length ? 'Снять все' : 'Выбрать все' }}
          </button>
          <button class="export-action-btn" @click="resetToDefault">По умолчанию</button>
        </div>
      </div>

      <div class="export-filters-section">
        <BaseCheckBox v-model="exportWithFilters" class="small-text">
          {{ filtersLabel }}
        </BaseCheckBox>
      </div>

      <div class="export-actions">
        <BaseButton
          variant="primary"
          size="large"
          :loading="props.store.isLoading"
          class="medium-text"
          @click="handleExport"
        >
          <template #icon-left>
            <ExportIcon />
          </template>
          Экспортировать в Excel
        </BaseButton>
      </div>

      <span v-if="exportError" class="export-error">
        {{ exportError }}
      </span>
    </div>
  </BaseCollapse>
</template>

<style scoped>
.export-body {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.export-columns {
  margin-bottom: 24px;
  text-align: center;
  width: 100%;
}

.export-subtitle {
  display: block;
  font: var(--medium-text);
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.export-group {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.export-group:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.export-group-title {
  display: block;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.columns-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.column-item {
  display: flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
  font-size: 13px;
}

.column-item:hover {
  border-color: var(--secondary);
  background: var(--white);
}

.export-columns-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 8px;
}

.export-action-btn {
  background: none;
  border: none;
  color: var(--secondary);
  cursor: pointer;
  font: var(--small-text);
  padding: 4px 8px;
  border-radius: 4px;
}

.export-action-btn:hover {
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
}

.export-filters-section {
  margin-bottom: 24px;
  padding: 14px 18px;
  border-radius: 8px;
  background: var(--color-background-soft);
  text-align: center;
}

.export-actions {
  display: flex;
  justify-content: center;
}

.export-error {
  display: block;
  margin-top: 16px;
  padding: 10px 16px;
  background: color-mix(in srgb, var(--error) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--error) 25%, transparent);
  border-radius: 8px;
  color: var(--error);
  font: var(--small-text);
  text-align: center;
}
</style>
