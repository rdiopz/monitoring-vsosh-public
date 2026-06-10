<script setup>
import { computed, defineAsyncComponent } from 'vue'
import AppHeader from '@/app/layout/AppHeader.vue'
import Sidebar from '@/app/layout/SideBar.vue'
import { useLocalStorage, useLocalStorageBoolean } from '@composables/useLocalStorage'

// Храним информация об состояниях в локальном хранилище
const activeSection = useLocalStorage('monitoring_active_section', 'olympiads')
const isSidebarCollapsed = useLocalStorageBoolean('monitoring_sidebar_collapsed', false)

// Изменение секции
const handleSectionChange = (sectionId) => {
  activeSection.value = sectionId
}

const handleSidebarToggle = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// Компоненты для каждого раздела
const sectionComponents = {
  olympiads: defineAsyncComponent(() => import('@operations/olympiads/OlympiadsSection.vue')),
  participants: defineAsyncComponent(
    () => import('@operations/participants/ParticipantsSection.vue'),
  ),
  subjects: defineAsyncComponent(() => import('@operations/subjects/SubjectsSection.vue')),
  schools: defineAsyncComponent(() => import('@operations/schools/SchoolsSection.vue')),
  municipalities: defineAsyncComponent(
    () => import('@operations/municipalities/MunicipalitiesSection.vue'),
  ),
  dashboard: defineAsyncComponent(() => import('@analysis/dashboard/DashboardSection.vue')),
  reports: defineAsyncComponent(() => import('@analysis/reports/ReportsSection.vue')),
  users: defineAsyncComponent(() => import('@admin/users/UsersSection.vue')),
  audit: defineAsyncComponent(() => import('@admin/audit/AuditSection.vue')),
  settings: defineAsyncComponent(() => import('@admin/settings/SettingsSection.vue')),
}

// Текущий активный компонент
const currentComponent = computed(() => {
  return sectionComponents[activeSection.value] || sectionComponents.olympiads
})

// Названия разделов для отображения
const sectionTitles = {
  olympiads: 'Участия во ВсОШ',
  participants: 'Участники олимпиад',
  subjects: 'Предметы олимпиад',
  schools: 'Образовательные учреждения',
  municipalities: 'Муниципалитеты',
  dashboard: 'Дашборд',
  reports: 'Отчёты',
  users: 'Управление пользователями',
  audit: 'Журнал аудита',
  settings: 'Настройки системы',
}

const currentHeaderTitle = computed(() => {
  return sectionTitles[activeSection.value] || sectionTitles.olympiads
})
</script>

<template>
  <div class="main-layout">
    <!-- Шапка -->
    <AppHeader
      :header-title="currentHeaderTitle"
      :is-sidebar-collapsed="isSidebarCollapsed"
      @toggle-sidebar="handleSidebarToggle"
    />

    <!-- Основная область -->
    <div class="main-area">
      <!-- Боковая панель -->
      <Sidebar :collapsed="isSidebarCollapsed" @section-change="handleSectionChange" />

      <!-- Контентная область -->
      <div class="content-area" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <!-- Динамический компонент раздела -->
        <div class="section-content">
          <Suspense>
            <component :is="currentComponent" />
            <template #fallback>
              <div class="loading-section">
                <div class="loading-spinner"></div>
                <p>Загрузка раздела...</p>
              </div>
            </template>
          </Suspense>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  width: 100vw;
  min-height: 100vh;
  background: var(--bg);
  overflow-x: hidden;
}

.main-area {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
  min-height: calc(100vh - 117px);
  background: var(--bg);
  margin-top: 117px;
}

.content-area {
  display: flex;
  flex-direction: column;
  padding: 0 15px 15px 15px;
  gap: 20px;
  width: calc(100% - 355px);
  margin-left: 355px;
  min-height: 100vh;
  background: var(--bg);
}

.content-area.sidebar-collapsed {
  margin-left: 70px;
  width: calc(100% - 70px);
}

/* Заголовок раздела */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 0 20px;
  border-bottom: 1px solid var(--on-dark);
}

/* Контент раздела */
.section-content {
  flex: 1;
  background: var(--white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

/* Загрузка */
.loading-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--primary);
  border-left: 4px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .content-area {
    padding: 0 10px 10px;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .section-title {
    font-size: 24px;
  }
}
</style>
