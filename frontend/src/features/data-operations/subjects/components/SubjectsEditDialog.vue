<script setup>
import { reactive, computed, watch } from 'vue'
import { useSubjectsStore } from '@entities/subjects'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  subject: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const subjectsStore = useSubjectsStore()

const editForm = reactive({
  id: null,
  full_name: '',
  short_name: '',
})

const canSave = computed(() => {
  return editForm.full_name.trim().length > 0 && editForm.short_name.trim().length > 0
})

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && props.subject) {
      editForm.id = props.subject.subject_id
      editForm.full_name = props.subject.full_name
      editForm.short_name = props.subject.short_name
    }
  },
)

const handleEditSubject = async () => {
  if (!canSave.value) return

  await subjectsStore.updateSubject(editForm.id, {
    full_name: editForm.full_name.trim(),
    short_name: editForm.short_name.trim(),
  })

  emit('update:modelValue', false)
}

const handleCancel = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Редактировать предмет"
    width="640px"
    :close-on-backdrop="false"
  >
    <form
      v-if="modelValue"
      id="edit-subject-form"
      @submit.prevent="handleEditSubject"
      class="edit-form"
    >
      <BaseInput
        v-model="editForm.full_name"
        type="text"
        label="Полное название"
        label-position="top"
        placeholder="Введите новое полное название"
        required
      />

      <BaseInput
        v-model="editForm.short_name"
        type="text"
        label="Краткое название"
        label-position="top"
        placeholder="Введите новое краткое название"
        required
      />
    </form>

    <template #footer>
      <div class="footer">
        <span v-if="editForm.id" class="footer-id">ID: {{ editForm.id }}</span>

        <div class="footer-actions">
          <BaseButton type="button" variant="outline" size="medium" @click="handleCancel">
            Отмена
          </BaseButton>

          <BaseButton
            type="submit"
            form="edit-subject-form"
            variant="primary"
            size="medium"
            :loading="subjectsStore.isLoading"
            :disabled="!canSave"
          >
            Сохранить
          </BaseButton>
        </div>
      </div>
    </template>
  </BaseDialog>
</template>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.footer {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.footer-id {
  font-size: 13px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .footer {
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
