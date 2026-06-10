<script setup>
import { ref, watch } from 'vue'
import { useApplicationsStore } from '@/entities/applications'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import BaseTextarea from '@ui/BaseTextarea.vue'
import BaseDialog from '@ui/BaseDialog.vue'
import { formatDateTime } from '@utils/date'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  application: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const appStore = useApplicationsStore()

const editForm = ref({
  email: '',
  new_password: '',
  review_comment: '',
  updated_at: '',
})

const showPassword = ref(false)

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.application) {
      editForm.value = {
        email: props.application.email,
        new_password: '',
        review_comment: props.application.review_comment || '',
        updated_at: props.application.updated_at || '',
      }
      showPassword.value = false
    }
  },
)

const handleSubmit = async () => {
  const data = {
    email: editForm.value.email,
    review_comment: editForm.value.review_comment,
  }

  if (editForm.value.new_password) {
    data.password = editForm.value.new_password
  }

  const result = await appStore.updateApplication(props.application.application_id, data)

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
    title="Редактирование заявки"
    width="550px"
    :close-on-backdrop="false"
  >
    <form
      v-if="application"
      id="edit-application-form"
      @submit.prevent="handleSubmit"
      class="dialog-form"
    >
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
        <label class="form-label">Новый пароль:</label>
        <BaseInput
          v-model="editForm.new_password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="Оставьте пустым"
          autocomplete="new-password"
        />
      </div>

      <BaseCheckBox v-model="showPassword" label="Показать пароль" />

      <BaseTextarea
        v-model="editForm.review_comment"
        label="Комментарий"
        label-position="top"
        placeholder="Комментарий"
        :rows="3"
      />
    </form>

    <template #footer>
      <div class="footer">
        <div class="meta">
          <span v-if="editForm.updated_at" class="meta-item">
            Обновлено: {{ formatDateTime(editForm.updated_at) }}
          </span>
        </div>

        <div class="footer-actions">
          <BaseButton variant="outline" @click="emit('update:modelValue', false)">
            Отмена
          </BaseButton>
          <BaseButton
            type="submit"
            form="edit-application-form"
            variant="primary"
            :loading="appStore.isLoading"
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

.footer {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.meta {
  display: flex;
  font-size: 13px;
  color: var(--text-secondary);
}

.meta-item {
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  gap: 12px;
}
</style>
