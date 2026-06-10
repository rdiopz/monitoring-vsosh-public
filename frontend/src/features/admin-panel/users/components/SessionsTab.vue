<script setup>
import { ref, onMounted } from 'vue'
import { useSessionsStore } from '@entities/sessions'
import { formatDateTime } from '@utils/date.js'

import SearchBar from '@/widgets/SearchBar/SearchBar.vue'
import FiltersPanel from '@/widgets/FiltersPanel/FiltersPanel.vue'

import BaseSelect from '@ui/BaseSelect.vue'
import BaseMultiSelect from '@ui/BaseMultiSelect.vue'
import BaseTable from '@ui/BaseTable.vue'
import BaseColumnToggle from '@ui/BaseColumnToggle.vue'
import BaseTag from '@ui/BaseTag.vue'
import BasePagination from '@ui/BasePagination.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseScrollableCell from '@ui/BaseScrollableCell.vue'

import ClearIcon from '@icons/actions/ClearIcon.vue'
import UsersIcon from '@icons/actions/PairUserIcon.vue'
import FingerprintIcon from '@icons/actions/FingerprintIcon.vue'

import SessionsDestroyDialog from './SessionsDestroyDialog.vue'
import SessionsRevokeFingerprintDialog from './SessionsRevokeFingerprintDialog.vue'
import SessionsRevokeUserDialog from './SessionsRevokeUserDialog.vue'

const sessionsStore = useSessionsStore()

const columns = [
  { key: 'jti', label: 'ID сессии', sortable: false, width: '100px', visible: false },
  { key: 'user_email', label: 'Email', sortable: false, width: '220px' },
  { key: 'user_id', label: 'User ID', sortable: false, width: '100px', visible: false },
  { key: 'device', label: 'Устройство', sortable: false },
  { key: 'browser', label: 'Браузер', sortable: false, width: '140px' },
  { key: 'platform', label: 'ОС', sortable: false, width: '120px' },
  { key: 'ip', label: 'IP адрес', sortable: false, width: '140px' },
  { key: 'fingerprint', label: 'Отпечаток', sortable: false, width: '200px' },
  { key: 'created_at', label: 'Начало сессии', sortable: false, width: '160px' },
  { key: 'last_activity', label: 'Активность', sortable: false, width: '160px' },
  { key: 'is_suspicious', label: 'Подозрительная', sortable: true, width: '120px' },
]

const localSuspiciousFilter = ref(null)
const localDeviceFilter = ref([])
const localBrowserFilter = ref([])
const localPlatformFilter = ref([])

const deviceOptions = [
  { label: 'Desktop', value: 'Desktop' },
  { label: 'Mobile', value: 'Mobile' },
  { label: 'Tablet', value: 'Tablet' },
  { label: 'Bot', value: 'Bot' },
]

const suspiciousOptions = [
  { label: 'Да', value: true },
  { label: 'Нет', value: false },
]

const destroyDialog = ref(false)
const revokeFingerprintDialog = ref(false)
const revokeUserDialog = ref(false)
const selectedSession = ref(null)

const loadSessions = () => {
  sessionsStore.fetchAllSessions()
}

// Сортировка
const handleSort = ({ key, order }) => {
  if (key === 'is_suspicious') {
    sessionsStore.ui.suspiciousFirst = order === 'asc'
  }
  sessionsStore.ui.page = 1
  loadSessions()
}

const applyFilters = () => {
  sessionsStore.ui.suspiciousFilter = localSuspiciousFilter.value
  sessionsStore.ui.deviceFilter = [...localDeviceFilter.value]
  sessionsStore.ui.browserFilter = [...localBrowserFilter.value]
  sessionsStore.ui.platformFilter = [...localPlatformFilter.value]
  sessionsStore.ui.page = 1
  loadSessions()
}

const resetFilters = () => {
  localSuspiciousFilter.value = null
  localDeviceFilter.value = []
  localBrowserFilter.value = []
  localPlatformFilter.value = []
  sessionsStore.ui.suspiciousFilter = null
  sessionsStore.ui.deviceFilter = []
  sessionsStore.ui.browserFilter = []
  sessionsStore.ui.platformFilter = []
  sessionsStore.ui.search = ''
  sessionsStore.ui.suspiciousFirst = true
  sessionsStore.ui.page = 1
  loadSessions()
}

const changePageSize = (size) => {
  sessionsStore.ui.pageSize = size
  sessionsStore.ui.page = 1
  loadSessions()
}

const changePage = (page) => {
  sessionsStore.ui.page = page
  loadSessions()
}

// Диалоги завершения сессий
const openDestroyDialog = (row) => {
  selectedSession.value = row
  destroyDialog.value = true
}

const openRevokeFingerprintDialog = (row) => {
  selectedSession.value = row
  revokeFingerprintDialog.value = true
}

const openRevokeUserDialog = (row) => {
  selectedSession.value = row
  revokeUserDialog.value = true
}

const onSessionDestroyed = () => {
  destroyDialog.value = false
  loadSessions()
}

const onFingerprintRevoked = () => {
  revokeFingerprintDialog.value = false
  loadSessions()
}

const onUserSessionsRevoked = () => {
  revokeUserDialog.value = false
  loadSessions()
}

// Инициализация
onMounted(async () => {
  localSuspiciousFilter.value = sessionsStore.ui.suspiciousFilter
  localDeviceFilter.value = [...sessionsStore.ui.deviceFilter]
  localBrowserFilter.value = [...sessionsStore.ui.browserFilter]
  localPlatformFilter.value = [...sessionsStore.ui.platformFilter]

  await loadSessions()
})
</script>

<template>
  <div class="sessions-tab">
    <SearchBar
      v-model="sessionsStore.ui.search"
      placeholder="Поиск по email, IP, JTI, fingerprint"
      :timeout="500"
      @search="applyFilters"
      class="search-bar"
    />

    <FiltersPanel :loading="sessionsStore.loading" @apply="applyFilters" @reset="resetFilters">
      <template #primary>
        <BaseSelect
          v-model="localSuspiciousFilter"
          placeholder="Подозрительные"
          :options="suspiciousOptions"
          height="44px"
          :clearable="true"
        />
        <BaseMultiSelect
          v-model="localDeviceFilter"
          placeholder="Устройства"
          :options="deviceOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="localBrowserFilter"
          placeholder="Браузеры"
          :options="sessionsStore.browserOptions"
          height="44px"
        />
        <BaseMultiSelect
          v-model="localPlatformFilter"
          placeholder="ОС"
          :options="sessionsStore.platformOptions"
          height="44px"
        />
      </template>
    </FiltersPanel>

    <div class="info-row">
      <div class="info-hint" tabindex="0">
        <span class="info-hint-icon">i</span>

        <div class="info-hint-popup">
          <div class="info-hint-title">Пояснения к колонкам</div>

          <div class="info-hint-block">
            <strong>Отпечаток</strong> — это технический идентификатор сессии, который формируется
            на сервере по совокупности параметров браузера и запроса: тип браузера, язык,
            поддерживаемые кодировки, платформа и другие служебные признаки. Он нужен не для
            идентификации человека, а для поиска похожих и связанных сессий.
          </div>

          <div class="info-hint-block">
            <strong>Подозрительная</strong> — сессия получает этот флаг автоматически, если при
            входе обнаружено одно из двух:
            <ul class="info-hint-list">
              <li>
                <strong>Несовпадение отпечатка</strong> — у пользователя уже есть активные сессии с
                другим отпечатком. Это может означать вход с нового браузера или устройства.
              </li>
              <li>
                <strong>Смена IP-адреса</strong> — у пользователя уже есть активные сессии с другим
                IP. Это может быть смена сети, VPN или вход из другого места.
              </li>
            </ul>
            <span class="info-also-text">
              Также отпечаток проверяется при каждом запросе: если текущий запрос перестал совпадать
              с отпечатком этой сессии, флаг тоже появится.
            </span>
          </div>

          <div class="info-hint-block">
            <strong>ID сессии</strong> — внутренний уникальный идентификатор конкретной сессии.
          </div>

          <div class="info-hint-block">
            <strong>Начало сессии</strong> — момент создания сессии, то есть когда пользователь
            выполнил вход и получил токен.
          </div>

          <div class="info-hint-block">
            <strong>Активность</strong> — время последнего действия в рамках этой сессии.
            Обновляется при каждом запросе. По нему видно, пользуется ли человек сессией сейчас или
            она давно простаивает.
          </div>

          <div class="info-hint-block">
            <strong>IP адрес</strong> — адрес сети, с которого пришёл запрос. Он помогает
            анализировать активность, но не всегда однозначно указывает на одного человека.
          </div>

          <div class="info-hint-block">
            <strong>User ID</strong> — внутренний идентификатор пользователя в системе.
          </div>
        </div>
      </div>
    </div>

    <BaseTable
      :columns="columns"
      :data="sessionsStore.sessions"
      :visible-columns="sessionsStore.ui.visibleColumns"
      :sort-by="'is_suspicious'"
      :sort-order="sessionsStore.ui.suspiciousFirst ? 'asc' : 'desc'"
      :loading="sessionsStore.loading"
      row-key="jti"
      empty-message="Сессии не найдены"
      @sort="handleSort"
    >
      <template #cell-jti="{ value }">
        <BaseScrollableCell :text="value" max-width="100px" nowrap />
      </template>

      <template #cell-device="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-browser="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-platform="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-ip="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-fingerprint="{ value }">
        <BaseScrollableCell :text="value" max-width="200px" nowrap />
      </template>

      <template #cell-user_email="{ value }">
        <BaseScrollableCell :text="value || 'Unknown'" max-width="220px" nowrap />
      </template>

      <template #cell-created_at="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #cell-last_activity="{ value }">
        {{ formatDateTime(value) }}
      </template>

      <template #cell-is_suspicious="{ value }">
        <BaseTag
          :label="value ? 'Да' : 'Нет'"
          :variant="value ? 'error' : 'success'"
          size="small"
        />
      </template>

      <template #actions="{ row }">
        <div class="actions-cell">
          <BaseIconButton
            variant="ghost"
            size="medium"
            label="Завершить сессии по отпечатку"
            @click="openRevokeFingerprintDialog(row)"
          >
            <FingerprintIcon />
          </BaseIconButton>
          <BaseIconButton
            variant="ghost"
            size="medium"
            label="Завершить все сессии пользователя"
            @click="openRevokeUserDialog(row)"
          >
            <UsersIcon />
          </BaseIconButton>
          <BaseIconButton
            variant="danger"
            size="medium"
            label="Завершить сессию"
            @click="openDestroyDialog(row)"
          >
            <ClearIcon />
          </BaseIconButton>
        </div>
      </template>

      <template #footer>
        <BaseColumnToggle
          :columns="columns"
          :model-value="sessionsStore.ui.visibleColumns"
          @update:model-value="sessionsStore.ui.visibleColumns = $event"
          position="top"
        />
        <BasePagination
          :model-value="sessionsStore.ui.page"
          :total-items="sessionsStore.total"
          :page-size="sessionsStore.ui.pageSize"
          @update:page-size="changePageSize"
          @update:model-value="changePage"
        />
      </template>
    </BaseTable>

    <SessionsDestroyDialog
      v-model="destroyDialog"
      :session="selectedSession"
      @destroyed="onSessionDestroyed"
    />

    <SessionsRevokeFingerprintDialog
      v-model="revokeFingerprintDialog"
      :session="selectedSession"
      @revoked="onFingerprintRevoked"
    />

    <SessionsRevokeUserDialog
      v-model="revokeUserDialog"
      :session="selectedSession"
      @revoked="onUserSessionsRevoked"
    />
  </div>
</template>

<style scoped>
.sessions-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-bar {
  margin-bottom: 8px;
}

.info-row {
  display: flex;
  justify-content: flex-end;
  margin-top: -4px;
  margin-bottom: 4px;
  position: relative;
  z-index: 10;
}

.info-hint {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.info-hint-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--white);
  color: var(--text-secondary);
  font: var(--semibold-head-text);
  line-height: 1;
  cursor: help;
  user-select: none;
  transition:
    border-color 0.15s ease,
    color 0.15s ease,
    background-color 0.15s ease,
    transform 0.15s ease;
}

.info-hint:hover .info-hint-icon,
.info-hint:focus-within .info-hint-icon {
  border-color: var(--color-border-hover);
  color: var(--primary);
  background: var(--color-background-soft);
  transform: translateY(-1px);
}

.info-hint-popup {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 440px;
  max-width: min(440px, calc(100vw - 32px));
  max-height: 460px;
  overflow-y: auto;
  padding: 16px 18px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--white);
  color: var(--text-primary);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
  font: var(--common-text);
  line-height: 1.55;
  scrollbar-width: thin;

  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transform: translateY(6px);
  transition:
    opacity 0.2s ease,
    visibility 0.2s ease,
    transform 0.2s ease;
}

.info-hint:hover .info-hint-popup,
.info-hint:focus-within .info-hint-popup {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translateY(0);
}

.info-hint-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.info-hint-block {
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.info-hint-block:last-child {
  margin-bottom: 0;
}

.info-hint-block strong {
  color: var(--text-primary);
  font-weight: 600;
}

.info-hint-list {
  margin: 8px 0 0;
  padding-left: 20px;
}

.info-hint-list li {
  margin-bottom: 6px;
  color: var(--text-secondary);
}

.info-hint-list li:last-child {
  margin-bottom: 0;
}

.info-also-text {
  display: block;
  margin-top: 8px;
}

.actions-cell {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 768px) {
  .sessions-tab {
    padding: 0;
  }

  .info-row {
    justify-content: flex-start;
  }

  .info-hint-popup {
    right: auto;
    left: 0;
    max-width: 440px;
    width: auto;
  }
}
</style>
