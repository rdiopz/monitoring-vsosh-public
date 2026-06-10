<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@entities/auth'
import { useSessionsStore } from '@entities/sessions'
import { formatDateTimeLong } from '@utils/date'

import BaseTag from '@ui/BaseTag.vue'
import BaseButton from '@/shared/ui/BaseButton.vue'

import UserIcon from '@icons/actions/PairUserIcon.vue'
import InformationIcon from '@icons/actions/InformationIcon.vue'
import DoorIcon from '@icons/actions/DoorIcon.vue'

import ProfileEmailCard from './components/ProfileEmailCard.vue'
import ProfilePasswordCard from './components/ProfilePasswordCard.vue'
import ProfileSessionsDialog from './components/ProfileSessionsDialog.vue'

const authStore = useAuthStore()
const sessionsStore = useSessionsStore()

const sessionsDialog = ref(false)

onMounted(async () => {
  if (!authStore.userCreatedAt) {
    await authStore.fetchProfile()
  }
  await sessionsStore.fetchSessions()
})

const openSessionsDialog = async () => {
  await sessionsStore.fetchSessions()
  sessionsDialog.value = true
}

const userRole = computed(() => authStore.userRole)
const accountCreatedAt = computed(() => authStore.userCreatedAt)
</script>

<template>
  <div class="profile-section">
    <span class="section-title large-text">Профиль</span>

    <div class="profile-grid">
      <div class="profile-main">
        <div class="info-card">
          <div class="info-header">
            <UserIcon class="info-icon" />
            <span class="info-title">Роль</span>
          </div>
          <div class="info-content">
            <BaseTag :label="userRole" variant="primary" size="large" />
          </div>
        </div>

        <ProfileEmailCard />

        <ProfilePasswordCard />

        <div class="info-card">
          <div class="info-header">
            <InformationIcon class="info-icon" />
            <span class="info-title">Информация</span>
          </div>
          <div class="info-content">
            <div class="account-info">
              <div class="info-row">
                <span class="info-label">Аккаунт создан:</span>
                <BaseTag variant="info" :label="formatDateTimeLong(accountCreatedAt)" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-side">
        <div class="info-card sessions-card">
          <div class="info-header">
            <DoorIcon class="info-icon" />
            <span class="info-title">Активные сессии</span>
          </div>
          <div class="info-content">
            <div class="sessions-preview">
              <div v-if="sessionsStore.sessions.length === 0" class="empty-sessions">
                <span class="empty-text">Нет активных сессий</span>
              </div>
              <template v-else>
                <div
                  v-for="session in sessionsStore.sessions.slice(0, 3)"
                  :key="session.jti"
                  class="session-item"
                >
                  <div class="session-info">
                    <span class="session-browser">{{ session.browser }}</span>
                    <span class="session-platform">{{ session.platform }}</span>
                    <span class="session-ip">{{ session.ip }}</span>
                  </div>
                  <BaseTag
                    v-if="session.is_current"
                    label="Текущая"
                    variant="success"
                    size="small"
                  />
                </div>
                <div v-if="sessionsStore.sessions.length > 3" class="more-sessions">
                  + ещё {{ sessionsStore.sessions.length - 3 }}
                </div>
                <BaseButton
                  variant="outline"
                  size="small"
                  @click="openSessionsDialog"
                  class="manage-sessions-btn"
                >
                  Управление сессиями
                </BaseButton>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ProfileSessionsDialog v-model="sessionsDialog" />
  </div>
</template>

<style scoped>
.profile-section {
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  color: var(--text-primary);
  margin: 0 0 32px;
  font-size: 28px;
  font-weight: 600;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background: var(--white);
  border: 1.5px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
}

.info-icon {
  width: 22px;
  height: 22px;
  color: var(--secondary);
  flex-shrink: 0;
}

.info-title {
  font: var(--medium-text);
  color: var(--text-primary);
  font-size: 15px;
}

.info-content {
  padding: 20px;
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  color: var(--text-secondary);
  font: var(--small-text);
  min-width: 140px;
}

.sessions-card {
  position: sticky;
  top: 24px;
}

.sessions-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-sessions {
  color: var(--text-tertiary);
  font: var(--small-text);
  font-style: italic;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-browser {
  font: var(--small-text);
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.session-platform,
.session-ip {
  font: var(--tiny-text);
  color: var(--text-secondary);
  font-size: 12px;
}

.more-sessions {
  color: var(--secondary);
  font: var(--small-text);
  font-weight: 500;
  padding: 8px 0;
}

.manage-sessions-btn {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .sessions-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .profile-section {
    padding: 20px 16px;
  }
  .section-title {
    font-size: 24px;
  }
}
</style>
