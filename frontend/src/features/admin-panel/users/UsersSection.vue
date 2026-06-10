<script setup>
import { computed } from 'vue'
import { useSectionState } from '@composables/useSectionState.js'
import { useUsersStore } from '@entities/users'
import { useApplicationsStore } from '@entities/applications'
import { useSessionsStore } from '@entities/sessions'

import BaseTabs from '@ui/BaseTabs.vue'

import UsersTab from './components/UsersTab.vue'
import ApplicationsTab from './components/ApplicationsTab.vue'
import SessionsTab from './components/SessionsTab.vue'

const usersStore = useUsersStore()
const applicationStore = useApplicationsStore()
const sessionsStore = useSessionsStore()

useSectionState('users', usersStore)
useSectionState('applications', applicationStore)
useSectionState('sessions', sessionsStore)

const tabs = [
  { value: 'users', label: 'Пользователи' },
  { value: 'applications', label: 'Заявки' },
  { value: 'sessions', label: 'Сессии' },
]

const activeTab = computed({
  get: () => usersStore.ui.activeTab,
  set: (val) => {
    usersStore.ui.activeTab = val
  },
})
</script>

<template>
  <div class="users-section">
    <BaseTabs v-model="activeTab" :tabs="tabs" />

    <div class="tab-content">
      <UsersTab v-show="activeTab === 'users'" />
      <ApplicationsTab v-show="activeTab === 'applications'" />
      <SessionsTab v-show="activeTab === 'sessions'" />
    </div>
  </div>
</template>

<style scoped>
.users-section {
  margin: 0 auto;
  padding: 0 40px;
}

.tab-content {
  padding-top: 40px;
}

@media (max-width: 768px) {
  .users-section {
    padding: 16px;
  }
}
</style>
