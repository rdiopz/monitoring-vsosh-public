<script setup>
import { ref, computed, onMounted } from 'vue'

import { useAuditStore } from '@entities/audit'

import { useSectionState } from '@composables/useSectionState.js'
import { formatDateTime } from '@utils/date.js'

import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'

import BaseInput from '@ui/BaseInput.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import BaseTable from '@ui/BaseTable.vue'
import BaseColumnToggle from '@ui/BaseColumnToggle.vue'
import BaseTag from '@ui/BaseTag.vue'
import BasePagination from '@ui/BasePagination.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseScrollableCell from '@ui/BaseScrollableCell.vue'

import FindIcon from '@icons/actions/FindIcon.vue'

import AuditLogDetailDialog from './components/AuditLogDetailDialog,.vue'

const auditStore = useAuditStore()

useSectionState('audit', auditStore)

const localActionFilter = ref([])
const localModelFilter = ref([])
const localDateFrom = ref(null)
const localDateTo = ref(null)
const localObjectIdFilter = ref('')

const auditColumns = [
  { key: 'log_id', label: 'ID', sortable: true, width: '100px' },
  { key: 'timestamp', label: 'Время', sortable: true, width: '190px' },
  { key: 'user_email', label: 'Пользователь', sortable: true, width: '400px' },
  { key: 'action', label: 'Действие', sortable: true, minWidth: '100px', width: '150px' },
  { key: 'model_name', label: 'Объект', sortable: true },
  { key: 'object_id', label: 'ID объекта', sortable: true },
  { key: 'ip_address', label: 'IP адрес', sortable: true },
]

const actionOptions = computed(() => auditStore.actionOptions)
const modelOptions = computed(() => auditStore.modelOptions)

const detailDialog = ref(false)
const selectedLog = ref(null)

const loadAuditLogs = () => {
  auditStore.fetchAuditLogs()
}

const handleSort = ({ key, order }) => {
  auditStore.ui.sortBy = key
  auditStore.ui.sortOrder = order
  auditStore.ui.page = 1
  loadAuditLogs()
}

const applyFilters = () => {
  auditStore.ui.actionFilter = [...localActionFilter.value]
  auditStore.ui.modelFilter = [...localModelFilter.value]
  auditStore.ui.dateFrom = localDateFrom.value
  auditStore.ui.dateTo = localDateTo.value
  auditStore.ui.objectIdFilter = localObjectIdFilter.value
  auditStore.ui.page = 1
  loadAuditLogs()
}

const resetFilters = () => {
  localActionFilter.value = []
  localModelFilter.value = []
  localDateFrom.value = null
  localDateTo.value = null
  localObjectIdFilter.value = ''
  auditStore.ui.actionFilter = []
  auditStore.ui.modelFilter = []
  auditStore.ui.dateFrom = null
  auditStore.ui.dateTo = null
  auditStore.ui.objectIdFilter = ''
  auditStore.ui.search = ''
  auditStore.ui.page = 1
  loadAuditLogs()
}

const changePageSize = (size) => {
  auditStore.ui.pageSize = size
  auditStore.ui.page = 1
  loadAuditLogs()
}

const parseJSON = (str) => {
  if (!str) return null
  try {
    return typeof str === 'string' ? JSON.parse(str) : str
  } catch {
    return str
  }
}

const openDetailDialog = (log) => {
  selectedLog.value = log
  detailDialog.value = true
}

onMounted(async () => {
  localActionFilter.value = [...auditStore.ui.actionFilter]
  localModelFilter.value = [...auditStore.ui.modelFilter]
  localDateFrom.value = auditStore.ui.dateFrom
  localDateTo.value = auditStore.ui.dateTo
  localObjectIdFilter.value = auditStore.ui.objectIdFilter

  await auditStore.fetchFilterOptions()
  await loadAuditLogs()
})
</script>

<template>
  <div class="audit-section">
    <SearchBar
      v-model="auditStore.ui.search"
      placeholder="Поиск по email, IP"
      :timeout="500"
      @search="applyFilters"
      class="search-bar"
    />

    <FiltersPanel
      :extended="auditStore.ui.filtersExtended"
      @update:extended="auditStore.ui.filtersExtended = $event"
      :loading="auditStore.loading"
      @apply="applyFilters"
      @reset="resetFilters"
    >
      <template #primary>
        <BaseMultiSelect
          v-model="localActionFilter"
          placeholder="Действия"
          :options="actionOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="localModelFilter"
          placeholder="Объекты"
          :options="modelOptions"
          height="44px"
        />
        <BaseInput
          v-model="localObjectIdFilter"
          placeholder="ID объекта"
          type="number"
          variant="tertiary"
          height="44px"
          validate-positive-integer
          class="id-input"
        />
      </template>

      <template #extended>
        <BaseDatePicker
          v-model="localDateFrom"
          placeholder="С даты"
          :enable-time="true"
          height="44px"
        />
        <BaseDatePicker
          v-model="localDateTo"
          placeholder="По дату"
          :enable-time="true"
          height="44px"
        />
      </template>
    </FiltersPanel>

    <BaseTable
      :columns="auditColumns"
      :data="auditStore.auditLogs"
      :visible-columns="auditStore.ui.visibleColumns"
      :sort-by="auditStore.ui.sortBy"
      :sort-order="auditStore.ui.sortOrder"
      :loading="auditStore.loading"
      row-key="log_id"
      expandable
      :expanded-rows="auditStore.ui.expandedRows"
      :actions-column-width="'100px'"
      empty-message="Логи аудита не найдены"
      @sort="handleSort"
      @update:expanded-rows="auditStore.ui.expandedRows = $event"
    >
      <template #cell-timestamp="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #cell-user_email="{ value }">
        <BaseScrollableCell :text="value" max-width="400px" nowrap />
      </template>

      <template #cell-action="{ value }">
        <BaseTag :label="value" variant="default" size="small" />
      </template>

      <template #actions="{ row }">
        <BaseIconButton
          variant="ghost"
          size="medium"
          label="Подробнее"
          @click="openDetailDialog(row)"
        >
          <FindIcon />
        </BaseIconButton>
      </template>

      <template #expanded="{ row }">
        <div class="expanded-content">
          <div class="detail-grid">
            <div class="detail-block">
              <span class="detail-title">Данные запроса</span>
              <pre class="detail-json">{{
                JSON.stringify(parseJSON(row.request_data), null, 2)
              }}</pre>
            </div>

            <div v-if="row.old_values" class="detail-block">
              <span class="detail-title">Старые значения</span>
              <pre class="detail-json">{{
                JSON.stringify(parseJSON(row.old_values), null, 2)
              }}</pre>
            </div>

            <div v-if="row.new_values" class="detail-block">
              <span class="detail-title">Новые значения</span>
              <pre class="detail-json">{{
                JSON.stringify(parseJSON(row.new_values), null, 2)
              }}</pre>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <BaseColumnToggle
          :columns="auditColumns"
          :model-value="auditStore.ui.visibleColumns"
          @update:model-value="auditStore.ui.visibleColumns = $event"
          position="top"
        />
        <BasePagination
          :model-value="auditStore.ui.page"
          :total-items="auditStore.total"
          :page-size="auditStore.ui.pageSize"
          @update:page-size="changePageSize"
          @update:model-value="
            (page) => {
              auditStore.ui.page = page
              loadAuditLogs()
            }
          "
        />
      </template>
    </BaseTable>

    <AuditLogDetailDialog v-model="detailDialog" :log="selectedLog" />
  </div>
</template>

<style scoped>
.audit-section {
  padding: 24px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 24px;
}

.id-input {
  min-width: 150px;
}

.expanded-content {
  padding: 20px 24px;
}

.detail-grid {
  display: grid;
  gap: 20px;
}

.detail-block {
  background: var(--color-background-soft);
  padding: 16px;
  border-radius: 8px;
}

.detail-title {
  display: block;
  font: var(--medium-text);
  color: var(--text-primary);
  margin-bottom: 12px;
}

.detail-json {
  margin: 0;
  padding: 12px;
  background: var(--color-background-mute);
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: var(--text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .audit-section {
    padding: 16px;
  }
}
</style>
