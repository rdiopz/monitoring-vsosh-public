<script setup>
import { ref, watch } from 'vue'
import { useUsersStore } from '@entities/users'
import { formatDateTime } from '@/shared/lib/utils/date'

import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  user: {
    type: Object,
    default: null,
  },
  roleOptions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const usersStore = useUsersStore()

const editForm = ref({
  email: '',
  new_password: '',
  role_id: null,
  is_active: true,
})

const showPassword = ref(false)

const getUserRoleId = (user) => {
  if (!user) return null
  if (user.role_id) return user.role_id

  if (user.role_name) {
    const role = props.roleOptions.find((r) => r.label === user.role_name)
    return role ? role.value : null
  }

  return null
}

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.user) {
      editForm.value = {
        email: props.user.email,
        new_password: '',
        role_id: getUserRoleId(props.user),
        is_active: props.user.is_active,
      }
      showPassword.value = false
    }
  },
)

const handleSubmit = async () => {
  const data = {
    email: editForm.value.email,
    is_active: editForm.value.is_active,
  }

  if (editForm.value.new_password) {
    data.password = editForm.value.new_password
  }

  if (editForm.value.role_id) {
    data.role = editForm.value.role_id
  }

  const result = await usersStore.updateUserPartial(props.user.user_id, data)

  if (result.success) {
    emit('update:modelValue', false)
    emit('saved')
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Редактирование пользователя"
    :close-on-backdrop="false"
    width="600px"
  >
    <form v-if="user" id="edit-user-form" @submit.prevent="handleSubmit" class="dialog-form">
      <div class="form-group">
        <label class="form-label">Email:</label>
        <BaseInput
          v-model="editForm.email"
          type="email"
          placeholder="email@example.com"
          autocomplete="off"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Роль:</label>
        <BaseSelect
          v-model="editForm.role_id"
          :options="roleOptions"
          placeholder="Выберите роль"
          searchable
        />
      </div>

      <BaseCheckBox v-model="editForm.is_active" label="Активен" />

      <div class="form-group">
        <label class="form-label">Новый пароль:</label>
        <BaseInput
          v-model="editForm.new_password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="Оставьте пустым"
          autocomplete="new-password"
        />
      </div>

      <BaseCheckBox v-model="showPassword" label="Показать пароль" />
    </form>

    <template #footer>
      <div class="footer-content">
        <div class="info-section">
          <span class="info-item"> Пароль: {{ formatDateTime(user?.password_changed_at) }} </span>
          <span class="info-item"> Обновлён: {{ formatDateTime(user?.updated_at) }} </span>
        </div>

        <div class="footer-actions">
          <BaseButton variant="outline" @click="emit('update:modelValue', false)">
            Отмена
          </BaseButton>

          <BaseButton
            type="submit"
            form="edit-user-form"
            variant="primary"
            :loading="usersStore.isLoading"
          >
            Сохранить
          </BaseButton>
        </div>
      </div>
    </template>
  </BaseDialog>
</template>

<style scoped>
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
  font: var(--medium-text);
}

.footer-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.info-section {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

.info-item {
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-actions {
    flex-direction: column;
  }

  .footer-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
