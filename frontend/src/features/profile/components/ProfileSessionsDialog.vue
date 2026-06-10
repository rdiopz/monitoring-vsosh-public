<script setup>
import { useSessionsStore } from '@entities/sessions'
import { formatDateTimeLong } from '@utils/date'
import BaseButton from '@ui/BaseButton.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import BaseDialog from '@ui/BaseDialog.vue'
import BaseTag from '@ui/BaseTag.vue'
import EmptyState from '@ui/EmptyState.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'

defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const sessionsStore = useSessionsStore()

const isCurrentSession = (session) => session.is_current

const revokeSession = async (jti) => {
  const result = await sessionsStore.revokeSession(jti)
  if (result.success) {
    await sessionsStore.fetchSessions()
  }
}

const logoutAll = async () => {
  const result = await sessionsStore.logoutAll()
  if (result.success) {
    await sessionsStore.fetchSessions()
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Активные сессии"
    width="700px"
  >
    <div class="sessions-dialog">
      <div class="sessions-header">
        <p class="sessions-info">
          Здесь отображаются все ваши активные сессии. Вы можете завершить любую сессию, кроме
          текущей.
        </p>
        <BaseButton
          v-if="sessionsStore.sessions.length > 1"
          variant="outline"
          size="small"
          @click="logoutAll"
        >
          Завершить все другие
        </BaseButton>
      </div>

      <EmptyState v-if="sessionsStore.sessions.length === 0" message="Нет активных сессий" />

      <div v-else class="sessions-list">
        <div
          v-for="session in sessionsStore.sessions"
          :key="session.jti"
          class="session-card"
          :class="{ 'session-card--current': isCurrentSession(session) }"
        >
          <div class="session-content">
            <div class="session-main">
              <div class="session-title-row">
                <span class="session-browser">{{ session.browser }}</span>
                <BaseTag
                  v-if="isCurrentSession(session)"
                  label="Текущая сессия"
                  variant="success"
                  size="small"
                />
              </div>
              <div class="session-details">
                <span class="session-detail">{{ session.platform }}</span>
                <span class="session-detail">{{ session.device }}</span>
                <span class="session-detail">{{ session.ip }}</span>
              </div>
            </div>

            <div class="session-dates">
              <div class="session-date-item">
                <span class="session-date-label">Начало:</span>
                <span class="session-date-value">{{ formatDateTimeLong(session.created_at) }}</span>
              </div>
              <div class="session-date-item">
                <span class="session-date-label">Активность:</span>
                <span class="session-date-value">{{
                  formatDateTimeLong(session.last_activity)
                }}</span>
              </div>
            </div>
          </div>

          <BaseIconButton
            v-if="!isCurrentSession(session)"
            variant="danger"
            size="medium"
            :with-transform="false"
            label="Завершить сессию"
            class="session-close-btn"
            @click="revokeSession(session.jti)"
          >
            <ClearIcon />
          </BaseIconButton>
        </div>
      </div>
    </div>
  </BaseDialog>
</template>

<style scoped>
.sessions-dialog {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sessions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.sessions-info {
  margin: 0;
  color: var(--text-secondary);
  font: var(--small-text);
  flex: 1;
  line-height: 1.5;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
}

.session-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 60px 16px 16px;
  background: var(--color-background-soft);
  border: 1.5px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.session-card:hover {
  border-color: var(--secondary);
}

.session-card--current {
  border-color: var(--success);
  background: color-mix(in srgb, var(--success) 5%, transparent);
}

.session-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.session-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.session-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.session-browser {
  font: var(--medium-text);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 15px;
}

.session-details {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.session-detail {
  color: var(--text-secondary);
  font: var(--tiny-text);
  font-size: 12px;
  padding: 2px 8px;
  background: var(--white);
  border-radius: 4px;
}

.session-dates {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.session-date-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-date-label {
  color: var(--text-secondary);
  font: var(--tiny-text);
  min-width: 70px;
}

.session-date-value {
  color: var(--text-primary);
  font: var(--small-text);
  font-size: 13px;
}

.session-close-btn {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
}

@media (max-width: 768px) {
  .sessions-header {
    flex-direction: column;
    align-items: stretch;
  }

  .session-card {
    padding: 16px 56px 16px 16px;
  }

  .session-close-btn {
    top: 50%;
    right: 12px;
    transform: translateY(-50%);
  }
}
</style>
