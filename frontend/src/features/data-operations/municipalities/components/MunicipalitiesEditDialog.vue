<script setup>
import { reactive, watch, computed } from 'vue'
import { useMunicipalitiesStore } from '@entities/municipalities'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  municipality: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const municipalitiesStore = useMunicipalitiesStore()

const editForm = reactive({
  id: null,
  name: '',
})

const canSave = computed(() => {
  return editForm.name.trim().length > 0
})

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && props.municipality) {
      editForm.id = props.municipality.municipality_id
      editForm.name = props.municipality.name
    }
  },
)

const handleEditMunicipality = async () => {
  if (!canSave.value) return

  await municipalitiesStore.updateMunicipality(editForm.id, {
    name: editForm.name.trim(),
  })

  emit('update:modelValue', false)
  editForm.id = null
  editForm.name = ''
}

const handleCancel = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Редактировать муниципалитет"
    width="640px"
    :close-on-backdrop="false"
  >
    <form
      v-if="modelValue"
      id="edit-municipality-form"
      @submit.prevent="handleEditMunicipality"
      class="edit-form"
    >
      <BaseInput
        v-model="editForm.name"
        type="text"
        label="Название муниципалитета"
        label-position="top"
        placeholder="Введите новое название"
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
            form="edit-municipality-form"
            variant="primary"
            size="medium"
            :loading="municipalitiesStore.isLoading"
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
