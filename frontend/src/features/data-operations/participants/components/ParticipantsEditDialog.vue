<script setup>
import { reactive, watch, computed } from 'vue'
import { useParticipantsStore } from '@entities/participants'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseRadioButton from '@ui/BaseRadioButton.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import BaseDialog from '@ui/BaseDialog.vue'
import { formatToISO, isoToDisplayDate } from '@utils/date'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  participant: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const participantsStore = useParticipantsStore()

const editForm = reactive({
  id: null,
  lastname: '',
  firstname: '',
  patronymic: '',
  birth_date: '',
  gender: 'М',
})

const canSave = computed(() => {
  return Boolean(
    editForm.lastname.trim() && editForm.firstname.trim() && editForm.birth_date && editForm.gender,
  )
})

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && props.participant) {
      editForm.id = props.participant.participant_id
      editForm.lastname = props.participant.lastname || ''
      editForm.firstname = props.participant.firstname || ''
      editForm.patronymic = props.participant.patronymic || ''
      editForm.birth_date = isoToDisplayDate(props.participant.birth_date)
      editForm.gender = props.participant.gender || 'М'
    }
  },
)

const handleEditParticipant = async () => {
  if (!canSave.value) return

  await participantsStore.updateParticipant(editForm.id, {
    lastname: editForm.lastname.trim(),
    firstname: editForm.firstname.trim(),
    patronymic: editForm.patronymic.trim() || null,
    birth_date: formatToISO(editForm.birth_date),
    gender: editForm.gender,
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
    title="Редактировать участника"
    width="680px"
    :close-on-backdrop="false"
  >
    <form
      v-if="modelValue"
      id="edit-participant-form"
      @submit.prevent="handleEditParticipant"
      class="edit-form"
    >
      <BaseInput
        v-model="editForm.lastname"
        type="text"
        label="Фамилия"
        label-position="top"
        placeholder="Фамилия"
        required
      />

      <BaseInput
        v-model="editForm.firstname"
        type="text"
        label="Имя"
        label-position="top"
        placeholder="Имя"
        required
      />

      <BaseInput
        v-model="editForm.patronymic"
        type="text"
        label="Отчество"
        label-position="top"
        placeholder="Отчество"
      />

      <div class="edit-form-row">
        <div class="date-column">
          <BaseDatePicker
            v-model="editForm.birth_date"
            mode="single"
            :enable-time="false"
            date-format="d.m.Y"
            placeholder="ДД.ММ.ГГГГ"
            label="Дата рождения"
            :clearable="true"
            open-up
          />
        </div>

        <div class="gender-column">
          <label class="gender-label small-text">Пол</label>
          <div class="gender-options">
            <BaseRadioButton v-model="editForm.gender" value="М" label="М" />
            <BaseRadioButton v-model="editForm.gender" value="Ж" label="Ж" />
          </div>
        </div>
      </div>
    </form>

    <template #footer>
      <BaseButton type="button" variant="outline" size="medium" @click="handleCancel">
        Отмена
      </BaseButton>

      <BaseButton
        type="submit"
        form="edit-participant-form"
        variant="primary"
        size="medium"
        :loading="participantsStore.isLoading"
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
  gap: 16px;
}

.edit-form-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.date-column {
  flex: 1;
  min-width: 220px;
}

.date-column :deep(.date-picker) {
  width: 100%;
  min-width: 0;
}

.gender-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 160px;
  justify-content: flex-start;
  padding-top: 8px;
}

.gender-label {
  color: var(--text-secondary);
}

.gender-options {
  display: flex;
  gap: 16px;
  align-items: center;
}

@media (max-width: 768px) {
  .edit-form-row {
    flex-direction: column;
  }

  .date-column,
  .gender-column {
    min-width: 0;
    width: 100%;
  }

  .gender-column {
    padding-top: 0;
  }
}
</style>
