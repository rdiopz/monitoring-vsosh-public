<script setup>
import { reactive, computed } from 'vue'
import { useParticipantsStore } from '@entities/participants'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseRadioButton from '@ui/BaseRadioButton.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import AddIcon from '@icons/actions/AddIcon.vue'
import { parseFullName } from '@utils/participants'
import { formatToISO } from '@utils/date'

const participantsStore = useParticipantsStore()

const addForm = reactive({
  full_name: '',
  birth_date: '',
  gender: 'М',
})

const canAddParticipant = computed(() => {
  const { lastname, firstname } = parseFullName(addForm.full_name)

  return Boolean(lastname && firstname && addForm.birth_date && addForm.gender)
})

const resetForm = () => {
  addForm.full_name = ''
  addForm.birth_date = ''
  addForm.gender = 'М'
}

const handleAddParticipant = async () => {
  const { lastname, firstname, patronymic } = parseFullName(addForm.full_name)
  if (!lastname || !firstname) return

  await participantsStore.createParticipant({
    lastname: lastname.trim(),
    firstname: firstname.trim(),
    patronymic: patronymic?.trim() || null,
    birth_date: formatToISO(addForm.birth_date),
    gender: addForm.gender,
  })

  resetForm()
}
</script>

<template>
  <form @submit.prevent="handleAddParticipant" class="add-form">
    <div class="form-field">
      <BaseInput
        v-model="addForm.full_name"
        type="text"
        label="ФИО"
        label-position="left"
        placeholder="Фамилия Имя Отчество"
        required
      />
      <div class="field-hint">Отчество можно не указывать, если его нет</div>
    </div>

    <div class="form-row">
      <div class="birth-date-wrapper">
        <BaseDatePicker
          v-model="addForm.birth_date"
          mode="single"
          :enable-time="false"
          date-format="d.m.Y"
          placeholder="ДД.ММ.ГГГГ"
          label="Дата рождения"
          :clearable="true"
        />
      </div>

      <div class="gender-column">
        <label class="gender-label small-text">Пол</label>
        <div class="gender-options">
          <BaseRadioButton v-model="addForm.gender" value="М" label="М" />
          <BaseRadioButton v-model="addForm.gender" value="Ж" label="Ж" />
        </div>
      </div>

      <div class="form-actions">
        <BaseButton type="button" variant="outline" size="medium" @click="resetForm">
          Сбросить
        </BaseButton>

        <BaseButton
          type="submit"
          variant="primary"
          size="medium"
          :loading="participantsStore.isLoading"
          :disabled="!canAddParticipant"
        >
          <template #icon-left>
            <AddIcon />
          </template>
          Добавить
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<style scoped>
.add-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
}

.form-field {
  width: 100%;
}

.field-hint {
  margin-top: 6px;
  margin-left: 120px;
  font-size: 12px;
  line-height: 1.35;
  color: var(--text-tertiary);
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.birth-date-wrapper {
  width: 220px;
  min-width: 220px;
}

.birth-date-wrapper :deep(.date-picker) {
  width: 100%;
  min-width: 0;
}

.gender-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 140px;
  padding-bottom: 8px;
}

.gender-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.gender-options {
  display: flex;
  gap: 16px;
  align-items: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-left: auto;
  padding-bottom: 8px;
}

@media (max-width: 900px) {
  .field-hint {
    margin-left: 0;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .birth-date-wrapper {
    width: 100%;
    min-width: 0;
  }

  .gender-column {
    padding-bottom: 0;
  }

  .form-actions {
    margin-left: 0;
    padding-bottom: 0;
  }

  .form-actions :deep(.base-button) {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .form-actions {
    flex-direction: column;
  }
}
</style>
