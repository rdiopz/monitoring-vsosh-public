<script setup>
import { computed, useSlots } from 'vue'
import SortAscIcon from '@icons/actions/SortAscIcon.vue'
import SortDescIcon from '@icons/actions/SortDescIcon.vue'
import SortIcon from '@icons/actions/SortIcon.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'
import ExpandAllIcon from '@icons/actions/ExpandAllIcon.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import EmptyState from '@ui/EmptyState.vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    default: () => [],
  },
  visibleColumns: {
    type: Array,
    default: null,
  },
  sortBy: {
    type: String,
    default: '',
  },
  sortOrder: {
    type: String,
    default: 'asc',
  },
  expandable: {
    type: Boolean,
    default: false,
  },
  expandedRows: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  emptyMessage: {
    type: String,
    default: 'Данные не найдены',
  },
  rowKey: {
    type: String,
    default: 'id',
  },
  actionsColumnWidth: {
    type: String,
    default: 'auto',
  },
})

const emit = defineEmits(['sort', 'update:expandedRows', 'expand-all'])

const slots = useSlots()

// Получение списка видимых колонок
const activeVisibleColumns = computed(() => {
  return props.visibleColumns ?? props.columns.map((c) => c.key)
})

// Получение данных видимых колонок
const visibleColumnsData = computed(() => {
  return props.columns.filter((col) => activeVisibleColumns.value.includes(col.key))
})

// Вспомогательная функция для получения ID строки
const getRowId = (row, index) => {
  const id = row[props.rowKey] ?? row.id
  if (id !== undefined && id !== null) {
    return String(id)
  }
  return `row-${index}`
}

// Данные с флагами
const preparedRows = computed(() => {
  return props.data.map((rowData, index) => {
    const rowId = getRowId(rowData, index)
    return {
      rowData,
      rowId,
      expanded: props.expandedRows.includes(rowId),
    }
  })
})

// Обработка сортировки
const handleSort = (key, sortable) => {
  if (!sortable) return
  const order = props.sortBy === key && props.sortOrder === 'asc' ? 'desc' : 'asc'
  emit('sort', { key, order })
}

// Для определения свойств колонки связанной с сортировкой
const getSortProps = (column) => {
  const active = props.sortBy === column.key
  const asc = props.sortOrder === 'asc'
  const label = column.label

  return {
    icon: active ? (asc ? SortAscIcon : SortDescIcon) : SortIcon,
    tooltip: column.sortable
      ? active
        ? asc
          ? 'По возрастанию'
          : 'По убыванию'
        : 'Сортировать'
      : '',
    ariaSort: column.sortable ? (active ? (asc ? 'ascending' : 'descending') : 'none') : undefined,
    ariaLabel: column.sortable
      ? active
        ? `${label} — ${asc ? 'по возрастанию' : 'по убыванию'}`
        : `${label} — сортировать`
      : label,
  }
}

// В объект добавляем вычисляемое свойство для каждого элемента
const columnsWithSortProps = computed(() => {
  return visibleColumnsData.value.map((column) => ({
    ...column,
    sortProps: getSortProps(column),
  }))
})

// Получение значения ячейки с поддержкой вложенных свойств
const getCellValue = (row, column) => {
  if (column.render) {
    return column.render(row)
  }
  const keys = column.key.split('.')
  return keys.reduce((obj, key) => obj?.[key], row)
}

// Нормализуем key в css-класс, чтобы точки из вложенных ключей (user.email)
const getCellClass = (key) => `cell--${String(key).replace(/\./g, '-')}`

// Поле для проверки раскрытия всех строк
const isExpandAll = computed(() => {
  const allRowIds = props.data.map((row, index) => getRowId(row, index))
  return allRowIds.length > 0 && allRowIds.every((id) => props.expandedRows.includes(id))
})

// Переключение состояния строки (развернуть/свернуть)
const toggleRow = (rowId) => {
  const index = props.expandedRows.indexOf(rowId)
  const newExpanded =
    index === -1 ? [...props.expandedRows, rowId] : props.expandedRows.filter((id) => id !== rowId)
  emit('update:expandedRows', newExpanded)
}

// Развернуть/свернуть все строки
const toggleAllRows = () => {
  const allRowIds = props.data.map((row, index) => getRowId(row, index))
  const allExpanded = allRowIds.every((id) => props.expandedRows.includes(id))
  emit('update:expandedRows', allExpanded ? [] : allRowIds)
  emit('expand-all', !allExpanded)
}
</script>

<template>
  <div class="table-container">
    <!-- Обертка таблицы с ограничением по высоте -->
    <div class="table-wrapper">
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <!-- Колонка для разворачивания (если включено) -->
              <th
                v-if="expandable"
                class="expand-column"
                :class="{
                  'expand-column--expanded': isExpandAll,
                }"
                :aria-label="isExpandAll ? 'Свернуть всё' : 'Развернуть всё'"
                :title="isExpandAll ? 'Свернуть всё' : 'Развернуть всё'"
                @click="toggleAllRows"
              >
                <span class="expand-column-icon">
                  <ExpandAllIcon />
                </span>
              </th>

              <!-- Динамические колонки -->
              <th
                v-for="column in columnsWithSortProps"
                :key="column.key"
                class="data-table-header-cell"
                :class="{ 'data-table-header-cell--sortable': column.sortable }"
                :style="{ width: column.width, minWidth: column.minWidth }"
                :aria-sort="column.sortProps.ariaSort"
                :aria-label="column.sortProps.ariaLabel"
                @click="handleSort(column.key, column.sortable)"
              >
                <div class="header-content" :title="column.sortProps.tooltip">
                  <span>{{ column.label }}</span>
                  <span v-if="column.sortable" class="sort-icon" aria-hidden="true">
                    <component :is="column.sortProps.icon" />
                  </span>
                </div>
              </th>

              <!-- Колонка действий -->
              <th
                v-if="$slots.actions"
                class="actions-column"
                :style="{ width: actionsColumnWidth }"
              >
                Действия
              </th>
            </tr>
          </thead>

          <tbody>
            <!-- Состояние загрузки -->
            <tr v-if="loading">
              <td
                :colspan="
                  visibleColumnsData.length + (expandable ? 1 : 0) + ($slots.actions ? 1 : 0)
                "
                class="table-empty-cell"
              >
                <BaseSpinner text="Загрузка..." />
              </td>
            </tr>

            <!-- Пустое состояние -->
            <tr v-else-if="data.length === 0">
              <td
                :colspan="
                  visibleColumnsData.length + (expandable ? 1 : 0) + ($slots.actions ? 1 : 0)
                "
                class="table-empty-cell"
              >
                <EmptyState :message="emptyMessage" />
              </td>
            </tr>

            <!-- Отображение данных -->
            <template v-else>
              <!-- eslint-disable vue/no-v-for-template-key -->
              <template v-for="row in preparedRows" :key="row.rowId">
                <!-- Основная строка. Клик по строке — только rowClick -->
                <tr class="data-table-row" :class="{ 'data-table-row--expanded': row.expanded }">
                  <!-- Ячейка для кнопки разворачивания -->
                  <td v-if="expandable" class="expand-cell" @click.stop="toggleRow(row.rowId)">
                    <button
                      class="expand-button"
                      :class="{ 'expand-button--expanded': row.expanded }"
                      :aria-label="row.expanded ? 'Свернуть' : 'Развернуть'"
                      :title="row.expanded ? 'Свернуть' : 'Развернуть'"
                    >
                      <span>
                        <ArrowDownIcon />
                      </span>
                    </button>
                  </td>

                  <!-- Ячейки данных -->
                  <td
                    v-for="column in visibleColumnsData"
                    :key="column.key"
                    class="data-table-cell"
                    :class="getCellClass(column.key)"
                  >
                    <slot
                      :name="`cell-${column.key}`"
                      :row="row.rowData"
                      :value="getCellValue(row.rowData, column)"
                    >
                      {{ getCellValue(row.rowData, column) }}
                    </slot>
                  </td>

                  <!-- Ячейка с действиями -->
                  <td v-if="$slots.actions" class="actions-cell" @click.stop>
                    <slot name="actions" :row="row.rowData"></slot>
                  </td>
                </tr>

                <!-- Развернутая строка с дополнительным контентом -->
                <tr v-if="expandable && slots.expanded && row.expanded" class="expanded-row">
                  <td class="expand-cell-empty"></td>
                  <td :colspan="visibleColumnsData.length + ($slots.actions ? 1 : 0)">
                    <div class="expanded-content">
                      <slot name="expanded" :row="row.rowData"></slot>
                    </div>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Нижняя часть таблицы -->
    <div v-if="$slots.footer" class="table-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<style scoped>
.table-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Обертка таблицы с ограничением высоты */
.table-wrapper {
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--white);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  scrollbar-width: thin;
  min-height: 0;
}

.data-table {
  width: 100%;
  table-layout: auto;
  border-collapse: collapse;
}

/* Закрепленные заголовки */
thead th {
  position: sticky;
  top: 0;
  z-index: 5;
  background-color: var(--head-color-table);
}

/* Ячейки заголовков */
.data-table-header-cell {
  padding: 1em;
  text-align: left;
  color: var(--text-primary);
  font: var(--head-text);
  letter-spacing: var(--letter-spacing-head);
  white-space: nowrap;
  border-bottom: 2px solid var(--color-border);
  overflow: hidden;
  text-overflow: ellipsis;
  background-color: var(--head-color-table);
}

/* Скругления углов таблицы */
thead tr:first-child th:first-child {
  border-radius: 12px 0 0 0;
}

thead tr:first-child th:last-child {
  border-radius: 0 12px 0 0;
}

.data-table-header-cell--sortable {
  cursor: pointer;
  user-select: none;
}

.data-table-header-cell--sortable:hover {
  background-color: var(--color-border);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  position: relative;
  z-index: 2;
}

.header-content span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sort-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1em;
  height: 1em;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.data-table-row {
  transition: background-color 0.2s ease;
}

.data-table-row:hover {
  background-color: var(--color-background-mute);
}

.data-table-row--expanded {
  background-color: var(--color-background);
}

/* Стили ячеек */
.data-table-cell {
  padding: 0.5em;
  border-bottom: 1px solid var(--color-border);
  color: var(--text-primary);
  font: var(--small-text);
  vertical-align: middle;
  overflow: hidden;
  max-width: 100%;
  min-width: 0;
}

/* Убираем нижнюю границу у последней строки */
tbody tr:last-child .data-table-cell,
tbody tr:last-child .actions-cell {
  border-bottom: none;
}

/* Раскрывающая колонка */
.expand-column {
  width: 24px !important;
  min-width: 24px !important;
  max-width: 24px !important;
  padding: 0 !important;
  cursor: pointer;
  text-align: center;
  user-select: none;
  background-color: var(--head-color-table);
  border-bottom: 2px solid var(--color-border);
  border-radius: 12px 0 0 0;
}

.expand-column:hover {
  background-color: var(--color-border);
}

/* Иконка разворачивания всех строк */
.expand-column-icon {
  width: 24px !important;
  min-width: 24px !important;
  max-width: 24px !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* эффект отскока */
}

.expand-column:hover .expand-column-icon {
  transform: scale(1.3);
  color: var(--secondary);
}

.expand-column--expanded .expand-column-icon {
  transform: scale(1.2);
  color: var(--secondary);
}

.expand-column--expanded:hover .expand-column-icon {
  transform: scale(0.9);
}

/* Ячейка с кнопкой разворачивания строки */
.expand-cell {
  width: 24px !important;
  min-width: 24px !important;
  max-width: 24px !important;
  padding: 0 !important;
  text-align: center;
  background-color: var(--white);
}

/* Кнопка разворачивания строки */
.expand-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
  color: var(--text-tertiary);
  flex: 0 0 24px;
}

.expand-button:hover {
  background: var(--color-border);
  color: var(--text-primary);
}

.expand-button--expanded {
  transform: rotate(90deg);
  color: var(--secondary);
}

.expand-button span {
  display: inline-flex;
  max-height: 16px;
  max-width: 16px;
  transform: rotate(270deg);
  align-items: center;
  justify-content: center;
}

/* Стили для колонки действий */
.actions-column {
  padding: 16px;
  text-align: right;
  background-color: var(--head-color-table);
  color: var(--text-primary);
  font: var(--head-text);
  letter-spacing: var(--letter-spacing-head);
  border-bottom: 2px solid var(--color-border);
  border-radius: 0 12px 0 0;
}

.actions-cell {
  padding: 0.4em;
  border-bottom: 1px solid var(--color-border);
  text-align: right;
}

.table-empty-cell {
  text-align: center;
  padding: 0;
}

.expanded-row {
  background: var(--color-background-soft);
}

.expand-cell-empty {
  width: 24px !important;
  min-width: 24px !important;
  max-width: 24px !important;
  padding: 0 !important;
  background-color: var(--white);
}

.expanded-content {
  padding: 20px 24px;
  border-collapse: collapse;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: nowrap;
  width: 100%;
}

@media (max-width: 1200px) {
  .table-footer {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .data-table th,
  .data-table td {
    padding: 0.4em;
    font-size: 14px;
  }

  .expand-cell {
    max-width: 24px;
    padding: 0;
  }

  .expand-column {
    max-width: 24px;
    padding: 0;
  }

  .table-footer {
    flex-wrap: wrap;
  }
}
</style>
