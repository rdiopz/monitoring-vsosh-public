<script setup>
import { reactive, computed } from 'vue'
import { useMunicipalitiesStore } from '@entities/municipalities'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import AddIcon from '@icons/actions/AddIcon.vue'

const municipalitiesStore = useMunicipalitiesStore()

const addForm = reactive({
  name: '',
})

const canAddMunicipality = computed(() => {
  return addForm.name.trim().length > 0
})

const resetForm = () => {
  addForm.name = ''
}

const handleAddMunicipality = async () => {
  if (!canAddMunicipality.value) return

  await municipalitiesStore.createMunicipality({
    name: addForm.name.trim(),
  })

  resetForm()
}
</script>

<template>
  <form @submit.prevent="handleAddMunicipality" class="add-form">
    <BaseInput
      v-model="addForm.name"
      type="text"
      label="Название"
      label-position="left"
      placeholder="Введите название муниципалитета"
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
        :loading="municipalitiesStore.isLoading"
        :disabled="!canAddMunicipality"
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
  gap: 16px;
  align-items: center;
  width: 100%;
}

.add-form :deep(.input-group) {
  flex: 1;
  min-width: 0;
  max-width: none;
}

.form-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .add-form {
    flex-direction: column;
    align-items: stretch;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
