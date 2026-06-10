<script setup>
import { reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@entities/auth'
import { useLocalStorage } from '@composables/useLocalStorage'
import CupIcon from '@icons/navigation/CupIcon.vue'
import ParticipantsIcon from '@icons/navigation/ParticipantsIcon.vue'
import BooksIcon from '@icons/navigation/SubjectsIcon.vue'
import SchoolIcon from '@icons/navigation/SchoolIcon.vue'
import MunicipalityIcon from '@icons/navigation/MunicipalityIcon.vue'
import DashboardIcon from '@icons/navigation/DashboardIcon.vue'
import ReportIcon from '@icons/navigation/ReportIcon.vue'
import UsersIcon from '@icons/navigation/UsersIcon.vue'
import AuditIcon from '@icons/navigation/AuditIcon.vue'
import SettingsIcon from '@icons/navigation/SettingsIcon.vue'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
})

const emit = defineEmits(['section-change'])

const authStore = useAuthStore()

// Проверка — администратор ли (для показа панели администрирования)
const isAdmin = computed(() => {
  const role = authStore.userRole
  return role === 'Администратор'
})

// Хранилище
const activeSection = useLocalStorage('monitoring_active_section', 'olympiads')

// Тултипы для свернутого меню
const tooltips = reactive({})
const tooltipPositions = reactive({})

// Структура меню
const allMenuSections = [
  {
    id: 'data',
    title: 'НАБОР ДАННЫХ',
    items: [
      { id: 'olympiads', name: 'Участия ВсОШ', icon: CupIcon },
      { id: 'participants', name: 'Участники', icon: ParticipantsIcon },
      { id: 'subjects', name: 'Предметы', icon: BooksIcon },
      { id: 'schools', name: 'Учреждения', icon: SchoolIcon },
      { id: 'municipalities', name: 'Муниципалитеты', icon: MunicipalityIcon },
    ],
  },
  {
    id: 'analytics',
    title: 'АНАЛИТИКА ДАННЫХ',
    items: [
      { id: 'dashboard', name: 'Дашборд', icon: DashboardIcon },
      { id: 'reports', name: 'Отчёты', icon: ReportIcon },
    ],
  },
  {
    id: 'administration',
    title: 'АДМИНИСТРИРОВАНИЕ',
    items: [
      { id: 'users', name: 'Пользователи', icon: UsersIcon },
      { id: 'audit', name: 'Аудит', icon: AuditIcon },
      { id: 'settings', name: 'Настройки', icon: SettingsIcon },
    ],
  },
]

// Фильтруем секции — администрирование видно только администратору
const menuSections = computed(() => {
  if (!isAdmin.value) {
    return allMenuSections.filter((s) => s.id !== 'administration')
  }
  return allMenuSections
})

// Все пункты плоским списком (для тултипов)
const allMenuItems = computed(() => menuSections.value.flatMap((section) => section.items))

const setActiveItem = (itemId) => {
  const isAvailable = allMenuItems.value.some((item) => item.id === itemId)
  if (isAvailable) {
    activeSection.value = itemId
    emit('section-change', itemId)
    return
  }

  const firstAvailable = allMenuItems.value[0]?.id || 'olympiads'
  if (activeSection.value !== firstAvailable) {
    activeSection.value = firstAvailable
    emit('section-change', firstAvailable)
  }
}

// Показать тултип при наведении на свернутый пункт
const showTooltip = (itemId, event) => {
  if (!props.collapsed) return

  const rect = event.currentTarget.getBoundingClientRect()
  tooltipPositions[itemId] = {
    top: rect.top + rect.height / 2,
    left: rect.right + 8,
  }
  tooltips[itemId] = true
}

const hideTooltip = (itemId) => {
  if (!props.collapsed) return
  tooltips[itemId] = false
}

const hideAllTooltips = () => {
  if (!props.collapsed) return
  Object.keys(tooltips).forEach((key) => {
    tooltips[key] = false
  })
}

const getTooltipStyle = (itemId) => {
  const pos = tooltipPositions[itemId]
  return pos ? { top: `${pos.top}px`, left: `${pos.left}px` } : {}
}

// При разворачивании меню чистим тултипы
watch(
  () => props.collapsed,
  (isCollapsed) => {
    if (!isCollapsed) hideAllTooltips()
  },
)

// При ресайзе тоже прячем
const handleResize = () => {
  if (props.collapsed) hideAllTooltips()
}

onMounted(() => {
  setActiveItem(activeSection.value)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="sidebar-wrapper">
    <!-- Боковое меню -->
    <div class="sidebar" :class="{ collapsed }" @mouseleave="hideAllTooltips">
      <div v-for="(section, idx) in menuSections" :key="section.id" class="sidebar-section">
        <!-- Заголовок секции (скрыт в свернутом виде) -->
        <div v-if="!collapsed" class="section-header">
          {{ section.title }}
        </div>

        <!-- Пункты меню -->
        <div
          v-for="item in section.items"
          :key="item.id"
          class="menu-item"
          :class="{ active: activeSection === item.id }"
          @click="setActiveItem(item.id)"
          @mouseenter="showTooltip(item.id, $event)"
          @mouseleave="hideTooltip(item.id)"
        >
          <component :is="item.icon" class="menu-icon" />
          <span v-if="!collapsed" class="menu-text">{{ item.name }}</span>
        </div>

        <!-- Разделитель (кроме последней секции) -->
        <div v-if="idx < menuSections.length - 1" class="section-divider" />
      </div>
    </div>

    <!-- Всплывающие подсказки для свернутого режима -->
    <div v-if="collapsed" class="tooltips-container">
      <div
        v-for="item in allMenuItems"
        :key="item.id"
        class="tooltip"
        :class="{ visible: tooltips[item.id] }"
        :style="getTooltipStyle(item.id)"
      >
        {{ item.name }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar-wrapper {
  position: relative;
}

.sidebar {
  position: fixed;
  top: 117px;
  bottom: 0;
  display: flex;
  flex-direction: column;
  width: 355px;
  background: var(--white);
  box-shadow:
    0 1px 2px var(--secondary),
    0 1px 3px var(--secondary);
  overflow-y: auto;
  transition: all 0.3s ease;
  z-index: 100;
}

.sidebar.collapsed {
  width: 70px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Заголовки секций */
.section-header {
  padding: 8px 24px;
  font: var(--head-text);
  letter-spacing: 0.05em;
  color: var(--secondary);
}

.sidebar.collapsed .section-header {
  display: none;
}

/* Пункты меню */
.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.sidebar.collapsed .menu-item {
  padding: 12px;
  justify-content: center;
}

.menu-item:hover {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
}

.menu-item.active {
  background: var(--gradient-side-tab);
  border-left: 3px solid var(--primary);
}

.menu-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.menu-text {
  font: var(--small-text);
  color: var(--dark);
}

.sidebar.collapsed .menu-text {
  display: none;
}

.menu-item.active .menu-text {
  color: var(--primary);
}

/* Разделители */
.section-divider {
  height: 1px;
  background: var(--secondary);
}

.sidebar.collapsed .section-divider {
  width: 70px;
}

/* Тултипы */
.tooltips-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 150;
}

.tooltip {
  position: absolute;
  background: var(--dark);
  color: var(--white);
  padding: 8px 12px;
  border-radius: 4px;
  font: var(--small-text);
  white-space: nowrap;
  opacity: 0;
  transform: translateY(-50%);
  transition: opacity 0.2s ease;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 151;
}

.tooltip.visible {
  opacity: 1;
}

/* Стрелочка у тултипа */
.tooltip::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
  border-right: 4px solid var(--dark);
}
</style>
