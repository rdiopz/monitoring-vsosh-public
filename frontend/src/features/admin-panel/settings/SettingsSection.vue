<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@entities/settings'
import { formatDateTimeShort } from '@utils/date'

import SearchBar from '@/widgets/SearchBar/SearchBar.vue'

import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import EmptyState from '@ui/EmptyState.vue'

import EditIcon from '@icons/actions/EditIcon.vue'
import CheckMarkIcon from '@icons/actions/CheckMarkIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import EyeOpenIcon from '@icons/actions/EyeOpenIcon.vue'
import EyeCloseIcon from '@icons/actions/EyeCloseIcon.vue'

const settingsStore = useSettingsStore()

const searchQuery = ref('')
const editingKey = ref(null)
const editValue = ref('')
const saveLoading = ref(null)
const hiddenKeys = ref(new Set(['registration_code']))

const isSecretKey = (key) => key === 'registration_code'

// Для скрытия секретных данных
const toggleHidden = (key) => {
  if (hiddenKeys.value.has(key)) {
    hiddenKeys.value.delete(key)
  } else {
    hiddenKeys.value.add(key)
  }
  hiddenKeys.value = new Set(hiddenKeys.value)
}

const isHidden = (key) => hiddenKeys.value.has(key)

// Клиентский поиск
const filteredSettings = computed(() => {
  if (!searchQuery.value) return settingsStore.settings
  const query = searchQuery.value.toLowerCase()
  return settingsStore.settings.filter(
    (s) =>
      s.key.toLowerCase().includes(query) ||
      s.description?.toLowerCase().includes(query) ||
      s.value.toLowerCase().includes(query),
  )
})

const startEdit = (setting) => {
  editingKey.value = setting.key
  editValue.value = setting.value
}

const cancelEdit = () => {
  editingKey.value = null
  editValue.value = ''
}

const saveEdit = async (setting) => {
  saveLoading.value = setting.key
  const result = await settingsStore.updateSetting(setting.key, { value: editValue.value })
  if (result.success) cancelEdit()
  saveLoading.value = null
}

onMounted(() => {
  settingsStore.fetchSettings()
})
</script>

<template>
  <div class="settings-section">
    <SearchBar v-model="searchQuery" placeholder="Поиск настроек..." class="search-bar" />

    <BaseSpinner v-if="settingsStore.loading" text="Загрузка..." />

    <EmptyState v-else-if="settingsStore.settings.length === 0" message="Настройки не найдены" />

    <div v-else class="settings-list">
      <div
        v-for="setting in filteredSettings"
        :key="setting.key"
        class="setting-card"
        :class="{ 'setting-card--editing': editingKey === setting.key }"
      >
        <div class="setting-description">
          <span class="setting-title">{{ setting.key }}</span>
          <span class="setting-text">{{ setting.description }}</span>
        </div>

        <div class="setting-input-wrapper">
          <template v-if="editingKey === setting.key">
            <div
              class="setting-input-container"
              :class="{ 'has-toggle': isSecretKey(setting.key) }"
            >
              <input
                v-model="editValue"
                class="setting-input"
                :type="isSecretKey(setting.key) && isHidden(setting.key) ? 'password' : 'text'"
                :placeholder="setting.value"
                autocomplete="new-password"
                autofocus
                @keyup.enter="saveEdit(setting)"
                @keyup.esc="cancelEdit()"
              />
              <button
                v-if="isSecretKey(setting.key)"
                class="input-toggle-btn"
                @click="toggleHidden(setting.key)"
                :title="isHidden(setting.key) ? 'Показать' : 'Скрыть'"
              >
                <EyeOpenIcon v-if="!isHidden(setting.key)" class="toggle-icon" />
                <EyeCloseIcon v-else class="toggle-icon" />
              </button>
            </div>
            <div class="setting-actions">
              <BaseIconButton
                variant="success"
                size="medium"
                label="Сохранить"
                :disabled="saveLoading === setting.key"
                @click="saveEdit(setting)"
              >
                <CheckMarkIcon />
              </BaseIconButton>
              <BaseIconButton variant="danger" size="medium" label="Отменить" @click="cancelEdit()">
                <ClearIcon />
              </BaseIconButton>
            </div>
          </template>

          <template v-else>
            <div class="setting-value-display">
              <span class="setting-value-text">
                {{ isSecretKey(setting.key) ? '••••••••' : setting.value }}
              </span>
            </div>
            <BaseIconButton
              variant="ghost"
              size="medium"
              label="Редактировать"
              @click="startEdit(setting)"
            >
              <EditIcon />
            </BaseIconButton>
          </template>
        </div>

        <div v-if="setting.updated_at" class="setting-meta">
          <span class="setting-meta-label">Обновлено:</span>
          <span class="setting-meta-value">{{ formatDateTimeShort(setting.updated_at) }}</span>
          <span class="setting-meta-user">{{ setting.updated_by__email }}</span>
        </div>
      </div>

      <EmptyState
        v-if="filteredSettings.length === 0 && settingsStore.settings.length > 0"
        message="Настройки не найдены"
      />
    </div>
  </div>
</template>

<style scoped>
.settings-section {
  padding: 24px;
  max-width: 1200px;
  height: 80vh;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 24px;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-card {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 24px;
  align-items: center;
  padding: 20px 24px;
  background: var(--white);
  border: 1.5px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.setting-card:hover {
  border-color: var(--secondary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.setting-card--editing {
  border-color: var(--primary);
  background: var(--color-background-soft);
  gap: 30px;
}

.setting-description {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-title {
  font: var(--medium-text);
  color: var(--secondary);
}

.setting-text {
  color: var(--text-secondary);
  font: var(--small-text);
  line-height: 1.6;
}

.setting-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
}

.setting-input-container {
  position: relative;
  flex: 1;
}

.setting-input-container.has-toggle .setting-input {
  padding-right: 44px;
}

.input-toggle-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.input-toggle-btn:hover {
  background: var(--color-background-soft);
}

.toggle-icon {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
}

.input-toggle-btn:hover .toggle-icon {
  color: var(--text-primary);
}

.setting-value-display {
  flex: 1;
  padding: 12px 16px;
  background: var(--color-background-soft);
  border-radius: 8px;
  cursor: default;
}

.setting-value-text {
  font: var(--small-text);
  color: var(--text-primary);
}

.setting-input {
  flex: 1;
  padding: 12px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  color: var(--text-primary);
  font: var(--small-text);
  outline: none;
  transition: border-color 0.3s ease;
  width: 100%;
}

.setting-input:focus {
  border-color: var(--primary);
}

.setting-actions {
  display: flex;
  gap: 8px;
}

.setting-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--color-background-mute);
  border-radius: 8px;
  font-size: 12px;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
}

.setting-card:hover .setting-meta {
  opacity: 1;
  transform: translateX(0);
}

.setting-meta-label {
  color: var(--text-tertiary);
  font-weight: 500;
}

.setting-meta-value {
  color: var(--text-secondary);
}

.setting-meta-user {
  color: var(--secondary);
  font-weight: 500;
}

@media (max-width: 1200px) {
  .setting-card {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .setting-input-wrapper {
    min-width: 100%;
  }

  .setting-meta {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
