<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useThemeStore } from '@stores/theme'
import { useAuthStore } from '@entities/auth'
import { useSettingsStore } from '@entities/settings'
import { useRouter } from 'vue-router'

import MoonIcon from '@icons/actions/MoonIcon.vue'
import SunIcon from '@icons/actions/SunIcon.vue'
import ShelvingIcon from '@icons/navigation/ShelvingIcon.vue'
import ClosedShelvingIcon from '@icons/navigation/ClosedShelvingIcon.vue'
import UserIcon from '@icons/navigation/OneUserIcon.vue'

const themeStore = useThemeStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const router = useRouter()

const isProfileDropDown = ref(false)

const props = defineProps({
  headerTitle: {
    type: String,
    default: 'Участия во ВсОШ',
  },
  isSidebarCollapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle-sidebar'])

const toggleTheme = () => themeStore.toggleTheme()

// Сворачивание/разворачивание сайдбара
const handleToggle = () => {
  emit('toggle-sidebar')
}

// Выпадающий список профиля
const toggleProfileDropDown = () => {
  isProfileDropDown.value = !isProfileDropDown.value
}

const closeProfileDropDown = () => {
  isProfileDropDown.value = false
}

const navigateToProfile = () => {
  router.push({ name: 'Profile' })
  closeProfileDropDown()
}

const handleLogout = async () => {
  await authStore.logout()
  closeProfileDropDown()
}

// Закрытие при клике вне области
const handleClickOutSide = (event) => {
  if (!event.target.closest('.profile-dropdown') && !event.target.closest('.profile-button')) {
    closeProfileDropDown()
  }
}

// Вычисляемые свойства
// Короткий email (обрезаем если длинный)
const safeEmail = computed(() => {
  const email = currentEmail?.trim() || ''
  if (!email) return ''

  const [username] = email.split('@')
  if (!username) return email

  const formattedUsername = username.toLowerCase()
  return formattedUsername.length > 15
    ? `${formattedUsername.substring(0, 15)}…`
    : formattedUsername
})

// Отображение годов мониторинга
const monitoringYearsText = computed(() => {
  const years = settingsStore.getSettingValue('monitoring_years')
  return years ? `${years} гг.` : '▢▢▢▢-▢▢▢▢ гг.'
})

// Данные пользователя из стора
const currentEmail = authStore.userEmail
const currentRole = authStore.userRole

onMounted(async () => {
  document.addEventListener('click', handleClickOutSide)
  await settingsStore.fetchMonitoringYears()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutSide)
})
</script>

<template>
  <header class="app-header">
    <!-- Левая часть: логотип и название -->
    <div class="header-left" :class="{ collapsed: isSidebarCollapsed }">
      <div class="logo-container">
        <img src="@/assets/logo_onfim.svg" alt="Логотип Онфим" class="logo" />
        <div class="logo-text">
          <span class="large-text text-on-header">
            Мониторинг <span class="text-accent">ВсОШ</span>
          </span>
          <span class="small-head-text" style="user-select: none"><br /></span>
          <span class="text-tertiary small-head-text">
            по Новгородской области<br />{{ monitoringYearsText }}
          </span>
        </div>
      </div>
    </div>

    <!-- Правая часть: навигация -->
    <div class="header-right">
      <!-- Кнопка сворачивания сайдбара -->
      <button class="nav-button" @click="handleToggle">
        <ShelvingIcon v-if="!isSidebarCollapsed" class="nav-icon" />
        <ClosedShelvingIcon v-else class="nav-icon" />
        <span class="nav-text">{{ props.headerTitle }}</span>
      </button>

      <!-- Блок управления (профиль + тема) -->
      <div class="header-controls">
        <!-- Выпадающий список профиля -->
        <div class="profile-container">
          <button class="profile-button" @click="toggleProfileDropDown">
            <UserIcon class="profile-icon" />
            <span class="profile-text">{{ safeEmail }}</span>
          </button>

          <!-- Выпадающий список с информацией о пользователе -->
          <div v-if="isProfileDropDown" class="profile-dropdown">
            <div class="dropdown-content">
              <!-- Шапка профиля -->
              <div class="dropdown-header">
                <UserIcon class="dropdown-icon" />
                <div class="dropdown-user-info">
                  <div class="dropdown-email">{{ safeEmail }}</div>
                  <div class="dropdown-role">{{ currentRole }}</div>
                </div>
              </div>
              <div class="dropdown-divider"></div>

              <!-- Кнопка перехода в профиль -->
              <button class="dropdown-item" @click="navigateToProfile">
                <div class="dropdown-item-content">
                  <div class="dropdown-item-text">Профиль</div>
                  <div class="dropdown-item-description">Настройки учетной записи</div>
                </div>
              </button>
              <div class="dropdown-divider"></div>

              <!-- Кнопка выхода -->
              <button class="dropdown-item logout" @click="handleLogout">
                <div class="dropdown-item-content">
                  <div class="dropdown-item-text">Выйти из аккаунта</div>
                  <div class="dropdown-item-description">Завершить текущую сессию</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- Переключатель темы (светлая/темная) -->
        <button class="theme-toggle" @click="toggleTheme" aria-label="Переключить тему">
          <MoonIcon v-if="!themeStore.isDark" />
          <SunIcon v-else />
          <span class="theme-text medium-text">Тема</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  z-index: 1000;
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  height: 117px;
  background: var(--gradient-header);
  border: 1px solid var(--secondary);
}

/* Левая часть с логотипом */
.header-left {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 0px;
  width: 355px;
  height: 117px;
  border-width: 0px 1px 1px 0px;
  border-style: solid;
  border-color: var(--secondary);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.header-left.collapsed {
  width: 70px;
}

.logo-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.header-left.collapsed .logo-container {
  gap: 0;
  justify-content: center;
}

.logo {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.header-left.collapsed .logo {
  width: 70px;
  height: 70px;
}

.logo-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
  opacity: 1;
  max-width: 230px;
}

.header-left.collapsed .logo-text {
  display: none;
}

/* Правая часть */
.header-right {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0px 32px 0px 16px;
  width: calc(100% - 355px);
  height: 85px;
  transition: all 0.3s ease;
}

.header-left.collapsed ~ .header-right {
  width: calc(100% - 70px);
}

/* Кнопка навигации */
.nav-button {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 10px;
  height: 50px;
  border-radius: 0px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.nav-button:hover {
  opacity: 0.8;
}

.nav-icon {
  width: 48px;
  height: 48px;
}

.nav-text {
  font: var(--large-text);
  display: flex;
  align-items: center;
  text-align: center;
  color: var(--on-header);
}

/* Блок управления */
.header-controls {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 48px;
  position: relative;
}

/* Профиль и выпадающий список */
.profile-container {
  position: relative;
}

.profile-button {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 8px 12px;
}

.profile-button:hover {
  opacity: 0.8;
}

.profile-icon {
  width: 48px;
  height: 48px;
}

.profile-text {
  font: var(--medium-text);
  display: flex;
  align-items: center;
  text-align: center;
  text-decoration: underline;
  color: var(--on-header);
}

/* Выпадающее меню */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 25px);
  left: 0px;
  min-width: 280px;
  background: var(--white);
  border: 1px solid var(--secondary);
  border-radius: 0px 0px 8px 8px;
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 1100;
  animation: dropdownFade 0.3s ease;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0px);
  }
}

.dropdown-content {
  padding: 16px 0;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px 12px 16px;
}

.dropdown-icon {
  width: 40px;
  height: 40px;
  color: var(--primary);
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
}

.dropdown-email {
  font: var(--small-text);
  color: var(--dark);
  font-weight: 500;
}

.dropdown-role {
  font: var(--tiny-text);
  color: var(--secondary);
}

.dropdown-divider {
  height: 1px;
  background: color-mix(in srgb, var(--secondary) 30%, transparent);
  margin: 12px 0;
}

.dropdown-item {
  display: flex;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  border-radius: 4px;
  margin: 0 8px;
}

.dropdown-item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-item-text {
  font: var(--small-text);
  color: var(--dark);
  font-weight: 500;
}

.dropdown-item-description {
  font: var(--tiny-text);
  color: var(--secondary);
}

.dropdown-item:hover {
  background: color-mix(in srgb, var(--secondary) 8%, transparent);
}

.dropdown-item.logout:hover {
  background: color-mix(in srgb, var(--error) 8%, transparent);
}

/* Переключатель темы */
.theme-toggle {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: var(--theme-button-color);
  border: 1px solid var(--secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: translateY(-1px);
}

.theme-toggle svg {
  color: var(--on-header);
}

.theme-text {
  color: var(--on-header);
}
</style>
