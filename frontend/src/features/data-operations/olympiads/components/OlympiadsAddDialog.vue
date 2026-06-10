<script setup>
import { reactive, computed, watch, ref } from 'vue'
import { useOlympiadsStore } from '@entities/olympiads'
import { useSchoolsStore } from '@entities/schools'
import { parseFullName, buildFullName } from '@utils/participants'
import { formatToISO } from '@utils/date'

import SearchParticipants from '@/widgets/SearchParticipants/SearchParticipants.vue'

import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import BaseRadioButton from '@ui/BaseRadioButton.vue'
import BaseDatePicker from '@ui/BaseDatePicker.vue'
import BasePillSelector from '@ui/BasePillSelector.vue'

import AddIcon from '@icons/actions/AddIcon.vue'

const olympiadsStore = useOlympiadsStore()
const schoolsStore = useSchoolsStore()

const addMode = ref('search')
const addFormKey = ref(0)

const addForm = reactive({
  participant: null,
  participant_full_name: '',
  participant_birth_date: '',
  participant_gender: 'М',
  municipality: null,
  education: null,
  subject: null,
  class_field: null,
  stage: 'ШЭ',
  status: 'участник',
  year: new Date().getFullYear(),
})

const municipalityOptions = computed(() =>
  olympiadsStore.filters.municipalities.map((m) => ({
    label: m.name,
    value: m.municipality_id,
  })),
)

const subjectOptions = computed(() =>
  olympiadsStore.filters.subjects.map((s) => ({
    label: s.full_name,
    value: s.subject_id,
  })),
)

const classOptions = computed(() =>
  olympiadsStore.filters.classes.map((c) => ({
    label: String(c),
    value: c,
  })),
)

const educationOptions = computed(() => {
  if (!addForm.municipality) return []

  return olympiadsStore.filters.educations
    .filter((e) => e.municipality === addForm.municipality)
    .map((e) => ({
      label: e.full_name,
      value: e.institution_id,
    }))
})

const canAdd = computed(() => {
  if (addMode.value === 'search') {
    return (
      addForm.participant &&
      addForm.municipality &&
      addForm.education &&
      addForm.subject &&
      addForm.class_field &&
      addForm.stage &&
      addForm.status &&
      addForm.year
    )
  }

  const { lastname, firstname } = parseFullName(addForm.participant_full_name)

  return (
    lastname &&
    firstname &&
    addForm.participant_birth_date &&
    addForm.participant_gender &&
    addForm.municipality &&
    addForm.education &&
    addForm.subject &&
    addForm.class_field &&
    addForm.stage &&
    addForm.status &&
    addForm.year
  )
})

// Заполняем поля скрытыми данными выбранного участника.
const onParticipantSelected = (participant) => {
  if (!participant) {
    addForm.participant_full_name = ''
    addForm.participant_birth_date = ''
    addForm.participant_gender = 'М'
    return
  }

  addForm.participant_full_name =
    participant.full_name ||
    buildFullName(participant.lastname, participant.firstname, participant.patronymic)
  addForm.participant_birth_date = participant.birth_date
  addForm.participant_gender = participant.gender
}

const resetForm = () => {
  Object.assign(addForm, {
    participant: null,
    participant_full_name: '',
    participant_birth_date: '',
    participant_gender: 'М',
    municipality: null,
    education: null,
    subject: null,
    class_field: null,
    stage: 'ШЭ',
    status: 'участник',
    year: new Date().getFullYear(),
  })

  addFormKey.value++
}

watch(addMode, () => {
  addForm.participant = null
  addForm.participant_full_name = ''
  addForm.participant_birth_date = ''
  addForm.participant_gender = 'М'
  addFormKey.value++
})

watch(
  () => addForm.municipality,
  async (val) => {
    // При смене муниципалитета старое учреждение сбрасываем.
    addForm.education = null

    if (val) {
      await schoolsStore.fetchSchools({ municipality: val, page_size: 500 })
    }
  },
)

const handleSubmit = async () => {
  if (!canAdd.value) return

  const payload = {
    education: addForm.education,
    subject: addForm.subject,
    class_field: addForm.class_field,
    stage: addForm.stage,
    status: addForm.status,
    year: addForm.year,
  }

  if (addMode.value === 'search' && addForm.participant) {
    payload.participant = addForm.participant
  } else {
    const { lastname, firstname, patronymic } = parseFullName(addForm.participant_full_name)

    payload.participant_lastname = lastname.trim()
    payload.participant_firstname = firstname.trim()

    const trimmedPatronymic = patronymic?.trim()
    if (trimmedPatronymic) {
      payload.participant_patronymic = trimmedPatronymic
    }

    payload.participant_birth_date = formatToISO(addForm.participant_birth_date)
    payload.participant_gender = addForm.participant_gender
  }

  await olympiadsStore.createParticipation(payload)
  resetForm()
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="add-form" :key="addFormKey">
    <div class="form-block">
      <div class="block-head">
        <span class="block-title">Участник</span>
        <span class="block-hint">
          {{
            addMode === 'search'
              ? 'Выберите уже зарегистрированного участника. При открытии поля будут показаны последние записи'
              : 'Заполни данные нового участника'
          }}
        </span>
      </div>

      <div class="mode-switch">
        <BaseRadioButton v-model="addMode" value="search" label="Выбрать" />
        <BaseRadioButton v-model="addMode" value="create" label="Создать" />
      </div>

      <div class="grid">
        <template v-if="addMode === 'search'">
          <div class="field full">
            <label class="field-label">Участник</label>
            <SearchParticipants
              v-model="addForm.participant"
              placeholder="ФИО или дата рождения..."
              @selected="onParticipantSelected"
            />
          </div>
        </template>

        <template v-else>
          <div class="field full">
            <label class="field-label">ФИО</label>
            <BaseInput
              v-model="addForm.participant_full_name"
              type="text"
              placeholder="Фамилия Имя Отчество"
              height="44px"
              required
            />
            <div class="field-hint">Отчество можно не указывать, если его нет</div>
          </div>

          <div class="field half">
            <label class="field-label">Дата рождения</label>
            <BaseDatePicker
              v-model="addForm.participant_birth_date"
              mode="single"
              :enable-time="false"
              date-format="d.m.Y"
              placeholder="ДД.ММ.ГГГГ"
              :clearable="true"
            />
          </div>

          <div class="field half">
            <label class="field-label">Пол</label>
            <div class="radio-line">
              <BaseRadioButton v-model="addForm.participant_gender" value="М" label="М" />
              <BaseRadioButton v-model="addForm.participant_gender" value="Ж" label="Ж" />
            </div>
          </div>
        </template>
      </div>
    </div>

    <div class="form-block">
      <div class="block-head">
        <span class="block-title">Учебная организация</span>
        <span class="block-hint">Организация, в которой участник обучался на тот момент</span>
      </div>

      <div class="grid">
        <div class="field half">
          <label class="field-label">Муниципалитет</label>
          <BaseSelect
            v-model="addForm.municipality"
            :options="municipalityOptions"
            placeholder="Муниципалитет"
            :searchable="true"
            :input-mode="true"
            :clearable="true"
          />
        </div>

        <div class="field half">
          <label class="field-label">Учреждение</label>
          <BaseSelect
            :key="addForm.municipality"
            v-model="addForm.education"
            :options="educationOptions"
            placeholder="Учреждение"
            :searchable="true"
            :input-mode="true"
            :clearable="true"
            :disabled="!addForm.municipality"
            max-height="360px"
          />
        </div>
      </div>
    </div>

    <div class="form-block">
      <div class="block-head">
        <span class="block-title">Результаты участия</span>
        <span class="block-hint">Данные о выступлении участника на конкретной олимпиаде</span>
      </div>

      <div class="grid">
        <div class="field half">
          <label class="field-label">Предмет</label>
          <BaseSelect
            v-model="addForm.subject"
            :options="subjectOptions"
            placeholder="Предмет"
            :searchable="true"
            :input-mode="true"
            :clearable="true"
          />
        </div>

        <div class="field quarter">
          <label class="field-label">Класс</label>
          <BaseSelect
            v-model="addForm.class_field"
            :options="classOptions"
            placeholder="Класс"
            :searchable="true"
            :input-mode="true"
            :clearable="true"
          />
        </div>

        <div class="field quarter">
          <label class="field-label">Год</label>
          <BaseInput
            v-model.number="addForm.year"
            type="number"
            inputmode="numeric"
            min="2000"
            max="2100"
            placeholder="2026"
            height="44px"
            validate-positive-integer
            required
          />
        </div>

        <div class="field half">
          <label class="field-label">Этап</label>
          <BasePillSelector
            v-model="addForm.stage"
            :options="[
              { value: 'ШЭ', color: 'var(--chart-stage-she)' },
              { value: 'МЭ', color: 'var(--chart-stage-me)' },
              { value: 'РЭ', color: 'var(--chart-stage-re)' },
              { value: 'ЗЭ', color: 'var(--chart-stage-ze)' },
            ]"
          />
        </div>

        <div class="field half">
          <label class="field-label">Статус</label>
          <BasePillSelector
            v-model="addForm.status"
            :options="[
              { value: 'победитель', color: 'var(--primary)' },
              { value: 'призёр', color: 'var(--secondary)' },
              { value: 'участник', color: 'var(--success)' },
            ]"
          />
        </div>
      </div>
    </div>

    <div class="actions">
      <BaseButton type="button" variant="outline" size="medium" @click="resetForm">
        Сбросить
      </BaseButton>

      <BaseButton
        type="submit"
        variant="primary"
        size="medium"
        :loading="olympiadsStore.isLoading"
        :disabled="!canAdd"
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
  gap: 14px;
}

.form-block {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 14px;
  background: var(--white);
}

.block-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.block-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.block-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.field-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.35;
  color: var(--text-tertiary);
}

.mode-switch {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border);
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 12px 14px;
}

.field {
  min-width: 0;
}

.full {
  grid-column: span 12;
}

.half {
  grid-column: span 6;
}

.quarter {
  grid-column: span 3;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.radio-line {
  display: flex;
  gap: 14px;
  min-height: 44px;
  align-items: center;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 960px) {
  .half,
  .quarter {
    grid-column: span 12;
  }

  .actions {
    flex-direction: column;
  }

  .actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
