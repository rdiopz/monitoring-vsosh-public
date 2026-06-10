<script setup>
import { reactive, computed } from 'vue'
import { useSubjectsStore } from '@entities/subjects'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import AddIcon from '@icons/actions/AddIcon.vue'

const subjectsStore = useSubjectsStore()

const addForm = reactive({
  full_name: '',
  short_name: '',
})

const canAddSubject = computed(() => {
  return addForm.full_name.trim().length > 0 && addForm.short_name.trim().length > 0
})

const resetForm = () => {
  addForm.full_name = ''
  addForm.short_name = ''
}

const handleAddSubject = async () => {
  if (!canAddSubject.value) return

  await subjectsStore.createSubject({
    full_name: addForm.full_name.trim(),
    short_name: addForm.short_name.trim(),
  })

  resetForm()
}
</script>

<template>
  <form @submit.prevent="handleAddSubject" class="add-form">
    <BaseInput
      v-model="addForm.full_name"
      type="text"
      label="Полное название"
      label-position="left"
      placeholder="Введите полное название предмета"
      required
    />

    <BaseInput
      v-model="addForm.short_name"
      type="text"
      label="Краткое название"
      label-position="left"
      placeholder="Введите краткое название"
      required
    />

    <div class="form-actions">
      <BaseButton type="button" variant="outline" size="medium" @click="resetForm">
        Сбросить
      </BaseButton>

      <BaseButton
        type="submit"
        variant="primary"
        size="medium"
        :loading="subjectsStore.isLoading"
        :disabled="!canAddSubject"
      >
        <template #icon-left>
          <AddIcon />
        </template>
        Добавить
      </BaseButton>
    </div>
  </form>
</template>

<style scoped>
.add-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.add-form :deep(.label--left .label-wrapper) {
  width: 200px;
  flex-shrink: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }

  .form-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
