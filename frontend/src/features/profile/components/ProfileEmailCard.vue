<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@entities/auth'
import BaseIconButton from '@ui/BaseIconButton.vue'
import EmailIcon from '@icons/actions/EmailIcon.vue'
import EditIcon from '@icons/actions/EditIcon.vue'
import CheckMarkIcon from '@icons/actions/CheckMarkIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'

const authStore = useAuthStore()

const isEditing = ref(false)
const emailValue = ref(authStore.userEmail)

const startEdit = () => {
  emailValue.value = authStore.userEmail
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
}

const saveEmail = async () => {
  const result = await authStore.updateProfilePartial({ email: emailValue.value })
  if (result) {
    isEditing.value = false
    await authStore.fetchProfile()
  }
}
</script>

<template>
  <div class="info-card">
    <div class="info-header">
      <EmailIcon class="info-icon" />
      <span class="info-title">Email</span>
    </div>
    <div class="info-content">
      <template v-if="isEditing">
        <div class="edit-field">
          <input
            v-model="emailValue"
            class="profile-input"
            type="email"
            placeholder="email@example.com"
            @keyup.enter="saveEmail"
            @keyup.esc="cancelEdit"
          />
          <div class="edit-actions">
            <BaseIconButton variant="success" size="medium" label="Сохранить" @click="saveEmail">
              <CheckMarkIcon />
            </BaseIconButton>
            <BaseIconButton variant="danger" size="medium" label="Отменить" @click="cancelEdit">
              <ClearIcon />
            </BaseIconButton>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="info-value">
          <span class="value-text">{{ authStore.userEmail }}</span>
          <BaseIconButton variant="ghost" size="medium" label="Изменить" @click="startEdit">
            <EditIcon />
          </BaseIconButton>
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

.info-value {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.value-text {
  font: var(--small-text);
  color: var(--text-primary);
  font-size: 15px;
  word-break: break-all;
}

.edit-field {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  color: var(--text-primary);
  font: var(--small-text);
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.profile-input:focus {
  border-color: var(--primary);
}

.edit-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .info-value {
    flex-direction: column;
    align-items: stretch;
  }
  .edit-field {
    flex-direction: column;
  }
  .edit-actions {
    justify-content: flex-end;
  }
}
</style>
