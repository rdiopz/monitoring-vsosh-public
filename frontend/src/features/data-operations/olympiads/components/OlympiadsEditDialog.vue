<script setup>
import { reactive, watch, ref, computed } from 'vue'
import { useOlympiadsStore } from '@entities/olympiads'
import { formatDateTime } from '@utils/date'
import { participantOptionLabel } from '@utils/participants'

import SearchParticipants from '@/widgets/SearchParticipants/SearchParticipants.vue'

import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import BaseDialog from '@ui/BaseDialog.vue'
import BasePillSelector from '@ui/BasePillSelector.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  participation: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const olympiadsStore = useOlympiadsStore()

const editForm = reactive({
  id: null,
  participant: null,
  municipality: null,
  education: null,
  subject: null,
  class_field: null,
  stage: '',
  status: '',
  year: null,
  created_at: '',
  updated_at: '',
})

const editFormKey = ref(0)
const isEditLoading = ref(false)
const participantInitialOption = ref(null)

const municipalityOptions = computed(() =>
  olympiadsStore.filters.municipalities.map((m) => ({
    label: m.name,
    value: m.municipality_id,
  })),
)

const subjectOptions = computed(() =>
  olympiadsStore.filters.subjects.map((s) => ({
    label: s.full_name,
    value: Number(s.subject_id),
  })),
)

const classOptions = computed(() =>
  olympiadsStore.filters.classes.map((c) => ({
    label: String(c),
    value: c,
  })),
)

// Учреждения берём из уже загруженных filters и фильтруем локально.
const educationOptions = computed(() => {
  if (!editForm.municipality) return []

  return olympiadsStore.filters.educations
    .filter((e) => Number(e.municipality) === Number(editForm.municipality))
    .map((e) => ({
      label: e.full_name,
      value: Number(e.institution_id),
    }))
})

const canSave = computed(() => {
  return (
    editForm.participant &&
    editForm.education &&
    editForm.subject &&
    editForm.class_field &&
    editForm.stage &&
    editForm.status &&
    editForm.year
  )
})

// Сбрасываем учреждение только при ручной смене муниципалитета.
const handleMunicipalityChange = (value) => {
  if (Number(value) !== Number(editForm.municipality)) {
    editForm.education = null
  }

  editForm.municipality = value
}

watch(
  () => props.modelValue,
  async (val) => {
    if (!val || !props.participation) return

    const row = props.participation
    isEditLoading.value = true

    try {
      Object.assign(editForm, {
        id: row.olymp_id,
        participant: row.participant ? Number(row.participant) : null,
        municipality: row.municipality ? Number(row.municipality) : null,
        education: row.education ? Number(row.education) : null,
        subject: row.subject ? Number(row.subject) : null,
        class_field: row.class_field,
        stage: row.stage || 'ШЭ',
        status: row.status || 'участник',
        year: row.year,
        created_at: row.created_at || '',
        updated_at: row.updated_at || '',
      })

      // Загрузажем участника
      participantInitialOption.value = row.participant
        ? {
            label: participantOptionLabel({
              full_name: row.participant_full_name,
              birth_date: row.participant_birth_date,
            }),
            value: Number(row.participant),
          }
        : null

      editFormKey.value++
    } catch (e) {
      console.error(e)
    } finally {
      isEditLoading.value = false
    }
  },
)

const handleSubmit = async () => {
  if (!canSave.value) return

  const payload = {
    participant: editForm.participant,
    education: editForm.education,
    subject: editForm.subject,
    class_field: editForm.class_field,
    stage: editForm.stage,
    status: editForm.status,
    year: editForm.year,
  }

  await olympiadsStore.updateParticipation(editForm.id, payload)
  emit('update:modelValue', false)
}

const handleCancel = () => emit('update:modelValue', false)
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Редактировать участие"
    width="860px"
    :close-on-backdrop="false"
  >
    <form
      v-if="modelValue"
      id="edit-form"
      @submit.prevent="handleSubmit"
      class="edit-form"
      :key="editFormKey"
    >
      <div class="edit-block">
        <span class="block-title">Участник</span>
        <div class="grid">
          <div class="field full">
            <label class="field-label">Участник</label>
            <SearchParticipants
              v-model="editForm.participant"
              :initial-option="participantInitialOption"
              placeholder="ФИО или дата рождения..."
            />
          </div>
        </div>
      </div>

      <div class="edit-block">
        <span class="block-title">Организация</span>
        <div class="grid">
          <div class="field half">
            <label class="field-label">Муниципалитет</label>
            <BaseSelect
              :model-value="editForm.municipality"
              :options="municipalityOptions"
              placeholder="Муниципалитет"
              :searchable="true"
              :input-mode="true"
              :clearable="true"
              @update:model-value="handleMunicipalityChange"
            />
          </div>

          <div class="field half">
            <label class="field-label">Учреждение</label>
            <BaseSelect
              :key="editForm.municipality"
              v-model="editForm.education"
              :options="educationOptions"
              placeholder="Учреждение"
              :searchable="true"
              :input-mode="true"
              :clearable="true"
              :disabled="!editForm.municipality"
              max-height="360px"
            />
          </div>
        </div>
      </div>

      <div class="edit-block">
        <span class="block-title">Олимпиада</span>
        <div class="grid">
          <div class="field half">
            <label class="field-label">Предмет</label>
            <BaseSelect
              v-model="editForm.subject"
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
              v-model="editForm.class_field"
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
              v-model.number="editForm.year"
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
              v-model="editForm.stage"
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
              v-model="editForm.status"
              :options="[
                { value: 'победитель', color: 'var(--primary)' },
                { value: 'призёр', color: 'var(--secondary)' },
                { value: 'участник', color: 'var(--success)' },
              ]"
            />
          </div>
        </div>
      </div>
    </form>

    <template #footer>
      <div class="footer">
        <div class="meta">
          <span v-if="editForm.created_at" class="meta-item">
            Создано: {{ formatDateTime(editForm.created_at) }}
          </span>
          <span v-if="editForm.updated_at" class="meta-item">
            Обновлено: {{ formatDateTime(editForm.updated_at) }}
          </span>
        </div>

        <div class="footer-actions">
          <BaseButton type="button" variant="outline" size="medium" @click="handleCancel">
            Отмена
          </BaseButton>
          <BaseButton
            type="submit"
            form="edit-form"
            variant="primary"
            size="medium"
            :loading="olympiadsStore.isLoading || isEditLoading"
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
  gap: 12px;
}

.edit-block {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: var(--white);
}

.block-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
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

.footer {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
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

@media (max-width: 960px) {
  .half,
  .quarter {
    grid-column: span 12;
  }

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
