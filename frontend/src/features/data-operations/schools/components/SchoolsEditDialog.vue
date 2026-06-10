<script setup>
import { reactive, computed, watch } from 'vue'
import { useSchoolsStore } from '@entities/schools'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import BaseTextarea from '@ui/BaseTextarea.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  school: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const schoolsStore = useSchoolsStore()

const editForm = reactive({
  id: null,
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

const canSave = computed(() => {
  return (
    editForm.municipality &&
    editForm.full_name.trim().length > 0 &&
    editForm.short_name.trim().length > 0
  )
})

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && props.school) {
      editForm.id = props.school.institution_id
      editForm.municipality = props.school.municipality
      editForm.full_name = props.school.full_name
      editForm.short_name = props.school.short_name || ''
    }
  },
)

const handleEditSchool = async () => {
  if (!canSave.value) return

  await schoolsStore.updateSchool(editForm.id, {
    municipality: editForm.municipality,
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
    title="Редактировать учреждение"
    width="700px"
    :close-on-backdrop="false"
  >
    <form
      v-if="modelValue"
      id="edit-school-form"
      @submit.prevent="handleEditSchool"
      class="edit-form"
    >
      <BaseSelect
        v-model="editForm.municipality"
        :options="municipalityOptions"
        placeholder="Выберите муниципалитет"
        label="Муниципалитет"
        :searchable="true"
        :input-mode="true"
        :clearable="true"
      />

      <BaseTextarea
        v-model="editForm.full_name"
        label="Полное наименование"
        label-position="top"
        placeholder="Введите новое полное наименование"
        :rows="3"
        required
      />

      <BaseInput
        v-model="editForm.short_name"
        type="text"
        label="Краткое наименование"
        label-position="top"
        placeholder="Введите новое краткое наименование"
        required
      />
    </form>

    <template #footer>
      <BaseButton type="button" variant="outline" size="medium" @click="handleCancel">
        Отмена
      </BaseButton>

      <BaseButton
        type="submit"
        form="edit-school-form"
        variant="primary"
        size="medium"
        :loading="schoolsStore.isLoading"
        :disabled="!canSave"
      >
        Сохранить
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.edit-form :deep(.select) {
  width: 100%;
  min-width: 0;
}
</style>
