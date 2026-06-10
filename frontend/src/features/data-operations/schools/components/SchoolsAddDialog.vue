<script setup>
import { reactive, computed, ref } from 'vue'
import { useSchoolsStore } from '@entities/schools'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import AddIcon from '@icons/actions/AddIcon.vue'

const schoolsStore = useSchoolsStore()

const addFormKey = ref(0)

const addForm = reactive({
  municipality: null,
  full_name: '',
  short_name: '',
})

const municipalityOptions = computed(() => {
  return schoolsStore.filters.municipalities.map((m) => ({
    label: m.name,
    value: m.municipality_id,
  }))
})

const canAddSchool = computed(() => {
  return (
    addForm.municipality &&
    addForm.full_name.trim().length > 0 &&
    addForm.short_name.trim().length > 0
  )
})

const resetForm = () => {
  addForm.municipality = null
  addForm.full_name = ''
  addForm.short_name = ''
  addFormKey.value++
}

const handleAddSchool = async () => {
  if (!canAddSchool.value) return

  await schoolsStore.createSchool({
    municipality: addForm.municipality,
    full_name: addForm.full_name.trim(),
    short_name: addForm.short_name.trim(),
  })

  resetForm()
}
</script>

<template>
  <form @submit.prevent="handleAddSchool" class="add-form" :key="addFormKey">
    <BaseSelect
      v-model="addForm.municipality"
      :options="municipalityOptions"
      placeholder="Выберите муниципалитет"
      label="Муниципалитет"
      :searchable="true"
      :input-mode="true"
      :clearable="true"
    />

    <BaseInput
      v-model="addForm.full_name"
      type="text"
      label="Полное наименование"
      label-position="top"
      placeholder="Введите полное наименование учреждения"
      required
    />

    <BaseInput
      v-model="addForm.short_name"
      type="text"
      label="Краткое наименование"
      label-position="top"
      placeholder="Введите краткое наименование"
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
        :loading="schoolsStore.isLoading"
        :disabled="!canAddSchool"
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
