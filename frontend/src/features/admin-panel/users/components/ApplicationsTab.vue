<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApplicationsStore } from '@/entities/applications.js'
import { useRolesStore } from '@entities/roles'
import { useUsersStore } from '@entities/users'
import { formatDateTime } from '@utils/date.js'
import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import BaseTable from '@ui/BaseTable.vue'
import BaseColumnToggle from '@ui/BaseColumnToggle.vue'
import BaseTag from '@ui/BaseTag.vue'
import BasePagination from '@ui/BasePagination.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseScrollableCell from '@ui/BaseScrollableCell.vue'
import CheckMarkIcon from '@icons/actions/CheckMarkIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import EditIcon from '@icons/actions/EditIcon.vue'
import TrashIcon from '@icons/actions/TrashIcon.vue'
import DeleteDialog from '@/widgets/DeleteDialog/DeleteDialog.vue'
import ApplicationApproveDialog from './ApplicationsApproveDialog.vue'
import ApplicationRejectDialog from './ApplicationsRejectDialog.vue'
import ApplicationEditDialog from './ApplicationsEditDialog.vue'

const appStore = useApplicationsStore()
const rolesStore = useRolesStore()
const usersStore = useUsersStore()

const columns = [
  { key: 'application_id', label: 'ID', sortable: true, width: '80px' },
  { key: 'email', label: 'Email', sortable: true, width: '240px' },
  { key: 'status', label: 'Статус', sortable: true, width: '100px' },
  { key: 'application_datetime', label: 'Дата подачи', sortable: true, width: '170px' },
  { key: 'review_comment', label: 'Комментарий', width: '250px' },
  { key: 'reviewed_by_email', label: 'Рассмотрел', sortable: true, width: '240px' },
  { key: 'updated_at', label: 'Обновлено', sortable: true, width: '180px', visible: false },
]

const localStatusFilter = ref([])
const localReviewedByFilter = ref([])
const localDateFrom = ref(null)
const localDateTo = ref(null)

const statusOptions = [
  { label: 'На рассмотрении', value: 'рассматривается' },
  { label: 'Одобрены', value: 'предоставлен' },
  { label: 'Отклонены', value: 'отклонён' },
]

const roleOptions = computed(() =>
  rolesStore.roles.map((r) => ({ label: r.name, value: r.role_id })),
)

const reviewerOptions = computed(() =>
  usersStore.reviewers.map((r) => ({ label: r.email, value: r.user_id })),
)

const approveDialog = ref(false)
const rejectDialog = ref(false)
const editDialog = ref(false)
const deleteDialog = ref(false)
const selectedApplication = ref(null)

const loadApplications = () => {
  appStore.fetchApplications()
}

const handleSort = ({ key, order }) => {
  appStore.ui.sortBy = key
  appStore.ui.sortOrder = order
  appStore.ui.page = 1
  loadApplications()
}

const applyFilters = () => {
  appStore.ui.statusFilter = [...localStatusFilter.value]
  appStore.ui.reviewedByFilter = [...localReviewedByFilter.value]
  appStore.ui.dateFrom = localDateFrom.value
  appStore.ui.dateTo = localDateTo.value
  appStore.ui.page = 1
  loadApplications()
}

const resetFilters = () => {
  localStatusFilter.value = []
  localReviewedByFilter.value = []
  localDateFrom.value = null
  localDateTo.value = null
  appStore.ui.statusFilter = []
  appStore.ui.reviewedByFilter = []
  appStore.ui.dateFrom = null
  appStore.ui.dateTo = null
  appStore.ui.search = ''
  appStore.ui.page = 1
  loadApplications()
}

const changePageSize = (size) => {
  appStore.ui.pageSize = size
  appStore.ui.page = 1
  loadApplications()
}

const changePage = (page) => {
  appStore.ui.page = page
  loadApplications()
}

// Статус: внешний вид
const getStatusVariant = (status) => {
  const map = {
    рассматривается: 'warning',
    предоставлен: 'success',
    отклонён: 'error',
  }
  return map[status] || 'default'
}

const getStatusLabel = (status) => {
  const map = {
    рассматривается: 'Рассмотрение',
    предоставлен: 'Одобрена',
    отклонён: 'Отклонена',
  }
  return map[status] || status
}

// Диалоги: открытие
const openApproveDialog = (row) => {
  selectedApplication.value = row
  approveDialog.value = true
}

const openRejectDialog = (row) => {
  selectedApplication.value = row
  rejectDialog.value = true
}

const openEditDialog = (row) => {
  selectedApplication.value = row
  editDialog.value = true
}

const openDeleteDialog = (row) => {
  selectedApplication.value = row
  deleteDialog.value = true
}

// Диалоги: успешное завершение
const onApproved = () => {
  approveDialog.value = false
  loadApplications()
}

const onRejected = () => {
  rejectDialog.value = false
  loadApplications()
}

const onSaved = () => {
  editDialog.value = false
  loadApplications()
}

const onDeleted = async () => {
  const result = await appStore.deleteApplication(selectedApplication.value.application_id)
  if (result.success) {
    deleteDialog.value = false
    loadApplications()
  }
}

// Инициализация
onMounted(async () => {
  localStatusFilter.value = [...appStore.ui.statusFilter]
  localReviewedByFilter.value = [...appStore.ui.reviewedByFilter]
  localDateFrom.value = appStore.ui.dateFrom
  localDateTo.value = appStore.ui.dateTo
  await rolesStore.fetchRoles()
  await usersStore.fetchReviewers()
  await loadApplications()
})
</script>

<template>
  <div class="applications-tab">
    <SearchBar
      v-model="appStore.ui.search"
      placeholder="Поиск по email, комментарию"
      :timeout="500"
      @search="applyFilters"
      class="search-bar"
    />

    <FiltersPanel
      :loading="appStore.loading"
      :extended="appStore.ui.filtersExtended"
      @update:extended="appStore.ui.filtersExtended = $event"
      @apply="applyFilters"
      @reset="resetFilters"
    >
      <template #primary>
        <BaseMultiSelect
          v-model="localStatusFilter"
          placeholder="Статусы"
          :options="statusOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="localReviewedByFilter"
          placeholder="Рассмотрел"
          :options="reviewerOptions"
          height="44px"
          class="xlarge"
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
      :columns="columns"
      :data="appStore.applications"
      :visible-columns="appStore.ui.visibleColumns"
      :sort-by="appStore.ui.sortBy"
      :sort-order="appStore.ui.sortOrder"
      :loading="appStore.loading"
      :actions-column-width="'170px'"
      row-key="application_id"
      empty-message="Заявки не найдены"
      @sort="handleSort"
    >
      <template #cell-email="{ value }">
        <BaseScrollableCell :text="value" max-width="240px" nowrap />
      </template>

      <template #cell-status="{ value }">
        <BaseTag :label="getStatusLabel(value)" :variant="getStatusVariant(value)" size="small" />
      </template>

      <template #cell-application_datetime="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #cell-review_comment="{ value }">
        <BaseScrollableCell :text="value" max-width="250px" max-height="40px" />
      </template>

      <template #cell-reviewed_by_email="{ value }">
        <BaseScrollableCell :text="value" max-width="240px" nowrap />
      </template>

      <template #cell-updated_at="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #actions="{ row }">
        <div class="actions-cell">
          <template v-if="row.status === 'рассматривается'">
            <BaseIconButton
              variant="success"
              size="medium"
              label="Принять"
              @click="openApproveDialog(row)"
            >
              <CheckMarkIcon />
            </BaseIconButton>
            <BaseIconButton
              variant="danger"
              size="medium"
              label="Отклонить"
              @click="openRejectDialog(row)"
            >
              <ClearIcon />
            </BaseIconButton>
          </template>
          <BaseIconButton
            variant="ghost"
            size="medium"
            label="Изменить"
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
          :model-value="appStore.ui.visibleColumns"
          @update:model-value="appStore.ui.visibleColumns = $event"
          position="top"
        />
        <BasePagination
          :model-value="appStore.ui.page"
          :total-items="appStore.total"
          :page-size="appStore.ui.pageSize"
          @update:page-size="changePageSize"
          @update:model-value="changePage"
        />
      </template>
    </BaseTable>

    <ApplicationApproveDialog
      v-model="approveDialog"
      :application="selectedApplication"
      :role-options="roleOptions"
      @approved="onApproved"
    />

    <ApplicationRejectDialog
      v-model="rejectDialog"
      :application="selectedApplication"
      @rejected="onRejected"
    />

    <ApplicationEditDialog
      v-model="editDialog"
      :application="selectedApplication"
      @saved="onSaved"
    />

    <DeleteDialog
      v-model="deleteDialog"
      entity-name="заявку"
      :item-name="selectedApplication?.email ?? ''"
      @confirm="onDeleted"
    />
  </div>
</template>

<style scoped>
.applications-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-bar {
  margin-bottom: 8px;
}

.comment-cell {
  display: block;
  max-width: 250px;
  max-height: 80px;
  overflow: auto;
  scrollbar-width: thin;
  color: var(--text-secondary);
}

.scrollable-text-cell {
  display: block;
  max-width: 200px;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  scrollbar-width: thin;
  color: var(--text-secondary);
  padding-bottom: 4px;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 100%;
}

@media (max-width: 768px) {
  .applications-tab {
    padding: 0;
  }
}
</style>
