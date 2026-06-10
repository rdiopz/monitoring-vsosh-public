<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@entities/auth'
import { useSessionsStore } from '@entities/sessions'
import { formatDateTimeLong } from '@utils/date'
import { getPasswordErrors } from '@utils/passwordRules'

import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseTag from '@ui/BaseTag.vue'
import LockIcon from '@icons/actions/LockIcon.vue'
import EyeIcon from '@icons/actions/EyeOpenIcon.vue'
import EyeOffIcon from '@icons/actions/EyeCloseIcon.vue'

const authStore = useAuthStore()
const sessionsStore = useSessionsStore()

const isChanging = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const showPasswords = ref({
  old_password: false,
  new_password: false,
  confirm_password: false,
})

const togglePasswordVisibility = (field) => {
  showPasswords.value[field] = !showPasswords.value[field]
}

const startChange = () => {
  passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  showPasswords.value = { old_password: false, new_password: false, confirm_password: false }
  isChanging.value = true
}

const cancelChange = () => {
  isChanging.value = false
}

const newPasswordErrors = computed(() => getPasswordErrors(passwordForm.value.new_password))

const confirmPasswordError = computed(() => {
  if (
    passwordForm.value.confirm_password &&
    passwordForm.value.new_password !== passwordForm.value.confirm_password
  ) {
    return 'Пароли не совпадают'
  }
  return null
})

const savePassword = async () => {
  const result = await authStore.changePassword(passwordForm.value)
  if (result) {
    await sessionsStore.fetchSessions()
    cancelChange()
  }
}

const passwordChangedAt = computed(() => authStore.userPasswordChangedAt)
</script>

<template>
  <div class="info-card">
    <div class="info-header">
      <LockIcon class="info-icon" />
      <span class="info-title">Безопасность</span>
    </div>
    <div class="info-content">
      <template v-if="isChanging">
        <div class="password-form">
          <div class="password-inputs">
            <BaseInput
              v-model="passwordForm.old_password"
              label="Текущий пароль"
              :type="showPasswords.old_password ? 'text' : 'password'"
              placeholder="Ваш текущий пароль"
            >
              <template #append>
                <button
                  class="toggle-btn"
                  @click="togglePasswordVisibility('old_password')"
                  type="button"
                  :title="showPasswords.old_password ? 'Скрыть' : 'Показать'"
                >
                  <EyeOffIcon v-if="showPasswords.old_password" class="toggle-icon" />
                  <EyeIcon v-else class="toggle-icon" />
                </button>
              </template>
            </BaseInput>

            <BaseInput
              v-model="passwordForm.new_password"
              label="Новый пароль"
              :type="showPasswords.new_password ? 'text' : 'password'"
              placeholder="Ваш новый пароль"
              :error="newPasswordErrors.length > 0 ? newPasswordErrors[0] : ''"
            >
              <template #append>
                <button
                  class="toggle-btn"
                  @click="togglePasswordVisibility('new_password')"
                  type="button"
                  :title="showPasswords.new_password ? 'Скрыть' : 'Показать'"
                >
                  <EyeOffIcon v-if="showPasswords.new_password" class="toggle-icon" />
                  <EyeIcon v-else class="toggle-icon" />
                </button>
              </template>
            </BaseInput>

            <BaseInput
              v-model="passwordForm.confirm_password"
              label="Подтверждение"
              :type="showPasswords.confirm_password ? 'text' : 'password'"
              placeholder="Повторите новый пароль"
              :error="confirmPasswordError"
            >
              <template #append>
                <button
                  class="toggle-btn"
                  @click="togglePasswordVisibility('confirm_password')"
                  type="button"
                  :title="showPasswords.confirm_password ? 'Скрыть' : 'Показать'"
                >
                  <EyeOffIcon v-if="showPasswords.confirm_password" class="toggle-icon" />
                  <EyeIcon v-else class="toggle-icon" />
                </button>
              </template>
            </BaseInput>
          </div>

          <div class="form-actions">
            <BaseButton variant="outline" size="small" @click="cancelChange">Отмена</BaseButton>
            <BaseButton
              variant="primary"
              size="small"
              @click="savePassword"
              :disabled="newPasswordErrors.length > 0 || !!confirmPasswordError"
            >
              Сохранить
            </BaseButton>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="password-info">
          <div class="password-row">
            <span class="password-label">Пароль:</span>
            <span class="password-dots">••••••••••••</span>
          </div>
          <div v-if="passwordChangedAt" class="password-row">
            <span class="password-label">Изменён:</span>
            <BaseTag variant="secondary" :label="formatDateTimeLong(passwordChangedAt)" />
          </div>
          <BaseButton variant="outline" size="small" @click="startChange">
            Изменить пароль
          </BaseButton>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
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

.password-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.password-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.password-label {
  color: var(--text-secondary);
  font: var(--small-text);
  min-width: 80px;
}

.password-dots {
  color: var(--text-primary);
  font: var(--small-text);
  font-size: 15px;
  letter-spacing: 2px;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.password-inputs {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.password-inputs {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.password-inputs :deep(.label--left) {
  align-items: center;
}

.password-inputs :deep(.label--left .label-wrapper) {
  width: 200px;
  flex-shrink: 0;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.toggle-btn:hover {
  opacity: 0.7;
}

.toggle-icon {
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
