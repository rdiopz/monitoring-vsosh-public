<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUsersStore } from '@entities/users'
import { useRolesStore } from '@entities/roles'
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

import EditIcon from '@icons/actions/EditIcon.vue'

import UsersEditDialog from './UsersEditDialog.vue'

const usersStore = useUsersStore()
const rolesStore = useRolesStore()

const columns = [
  { key: 'user_id', label: 'ID', sortable: true, width: '80px' },
  { key: 'email', label: 'Email', sortable: true, width: '350px' },
  { key: 'role_name', label: 'Роль', sortable: true, width: '200px' },
  { key: 'last_login', label: 'Последний вход', sortable: true, width: '200px' },
  { key: 'created_at', label: 'Создан', sortable: true, width: '200px' },
  { key: 'is_active', label: 'Статус', sortable: true, width: '120px' },
]

const localRoleFilter = ref([])
const localStatusFilter = ref([])
const localLastLoginFrom = ref(null)
const localLastLoginTo = ref(null)
const localCreatedFrom = ref(null)
const localCreatedTo = ref(null)

const statusOptions = [
  { label: 'Активен', value: 'true' },
  { label: 'Неактивен', value: 'false' },
]

const editDialog = ref(false)
const selectedUser = ref(null)

const openEditDialog = (user) => {
  selectedUser.value = user
  editDialog.value = true
}

const loadUsers = () => {
  usersStore.fetchUsers()
}

const handleSort = ({ key, order }) => {
  usersStore.ui.sortBy = key
  usersStore.ui.sortOrder = order
  usersStore.ui.page = 1
  loadUsers()
}

const applyFilters = () => {
  usersStore.ui.roleFilter = [...localRoleFilter.value]
  usersStore.ui.statusFilter = [...localStatusFilter.value]
  usersStore.ui.lastLoginFrom = localLastLoginFrom.value
  usersStore.ui.lastLoginTo = localLastLoginTo.value
  usersStore.ui.createdFrom = localCreatedFrom.value
  usersStore.ui.createdTo = localCreatedTo.value
  usersStore.ui.page = 1
  loadUsers()
}

const resetFilters = () => {
  localRoleFilter.value = []
  localStatusFilter.value = []
  localLastLoginFrom.value = null
  localLastLoginTo.value = null
  localCreatedFrom.value = null
  localCreatedTo.value = null
  usersStore.ui.roleFilter = []
  usersStore.ui.statusFilter = []
  usersStore.ui.lastLoginFrom = null
  usersStore.ui.lastLoginTo = null
  usersStore.ui.createdFrom = null
  usersStore.ui.createdTo = null
  usersStore.ui.search = ''
  usersStore.ui.page = 1
  loadUsers()
}

const changePageSize = (size) => {
  usersStore.ui.pageSize = size
  usersStore.ui.page = 1
  loadUsers()
}

const roleOptions = computed(() =>
  rolesStore.roles.map((r) => ({
    label: r.name,
    value: r.role_id,
  })),
)

onMounted(async () => {
  localRoleFilter.value = [...usersStore.ui.roleFilter]
  localStatusFilter.value = [...usersStore.ui.statusFilter]
  localLastLoginFrom.value = usersStore.ui.lastLoginFrom
  localLastLoginTo.value = usersStore.ui.lastLoginTo
  localCreatedFrom.value = usersStore.ui.createdFrom
  localCreatedTo.value = usersStore.ui.createdTo

  await rolesStore.fetchRoles()
  await loadUsers()
})
</script>

<template>
  <div class="users-tab">
    <SearchBar
      v-model="usersStore.ui.search"
      placeholder="Поиск по email, роли"
      :timeout="500"
      @search="applyFilters"
      class="search-bar"
    />

    <FiltersPanel
      :extended="usersStore.ui.filtersExtended"
      @update:extended="usersStore.ui.filtersExtended = $event"
      :loading="usersStore.loading"
      @apply="applyFilters"
      @reset="resetFilters"
    >
      <template #primary>
        <BaseMultiSelect
          v-model="localRoleFilter"
          placeholder="Роли"
          :options="roleOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="localStatusFilter"
          placeholder="Статусы"
          :options="statusOptions"
          height="44px"
        />
      </template>

      <template #extended>
        <BaseDatePicker
          v-model="localLastLoginFrom"
          placeholder="Последний вход с"
          :enable-time="true"
          height="44px"
        />
        <BaseDatePicker
          v-model="localLastLoginTo"
          placeholder="Последний вход по"
          :enable-time="true"
          height="44px"
        />
        <BaseDatePicker
          v-model="localCreatedFrom"
          placeholder="Дата создания с"
          :enable-time="true"
          height="44px"
        />
        <BaseDatePicker
          v-model="localCreatedTo"
          placeholder="Дата создания по"
          :enable-time="true"
          height="44px"
        />
      </template>
    </FiltersPanel>

    <BaseTable
      :columns="columns"
      :data="usersStore.users"
      :visible-columns="usersStore.ui.visibleColumns"
      :sort-by="usersStore.ui.sortBy"
      :sort-order="usersStore.ui.sortOrder"
      :loading="usersStore.loading"
      :actions-column-width="'120px'"
      row-key="user_id"
      empty-message="Пользователи не найдены"
      @sort="handleSort"
    >
      <template #cell-is_active="{ value }">
        <BaseTag
          :label="value ? 'Активен' : 'Неактивен'"
          :variant="value ? 'success' : 'default'"
          size="small"
        />
      </template>

      <template #cell-email="{ value }">
        <BaseScrollableCell :text="value" max-width="350px" nowrap />
      </template>

      <template #cell-last_login="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #cell-created_at="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #actions="{ row }">
        <BaseIconButton
          variant="ghost"
          size="medium"
          label="Редактировать"
          @click="openEditDialog(row)"
        >
          <EditIcon />
        </BaseIconButton>
      </template>

      <template #footer>
        <BaseColumnToggle
          :columns="columns"
          :model-value="usersStore.ui.visibleColumns"
          @update:model-value="usersStore.ui.visibleColumns = $event"
          position="top"
        />
        <BasePagination
          :model-value="usersStore.ui.page"
          :total-items="usersStore.total"
          :page-size="usersStore.ui.pageSize"
          @update:page-size="changePageSize"
          @update:model-value="
            (page) => {
              usersStore.ui.page = page
              loadUsers()
            }
          "
        />
      </template>
    </BaseTable>

    <UsersEditDialog
      v-model="editDialog"
      :user="selectedUser"
      :role-options="roleOptions"
      @saved="loadUsers"
    />
  </div>
</template>

<style scoped>
.users-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-bar {
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .users-tab {
    padding: 0;
  }
}
</style>
