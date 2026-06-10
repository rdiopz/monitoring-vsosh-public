<script setup>
import { ref, watch, computed } from 'vue'
import { useApplicationsStore } from '@/entities/applications'
import BaseButton from '@ui/BaseButton.vue'
import BaseSelect from '@ui/BaseSelect.vue'
import BaseTextarea from '@ui/BaseTextarea.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  application: {
    type: Object,
    default: null,
  },
  roleOptions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'approved'])

const appStore = useApplicationsStore()

const form = ref({
  role_id: null,
  review_comment: '',
})

const canSubmit = computed(() => Boolean(form.value.role_id))

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      form.value = { role_id: null, review_comment: '' }
    }
  },
)

const handleSubmit = async () => {
  if (!canSubmit.value) return

  const result = await appStore.approveApplication(props.application.application_id, form.value)

  if (result.success) {
    emit('update:modelValue', false)
    emit('approved')
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Одобрение заявки"
    width="500px"
    :close-on-backdrop="false"
  >
    <form v-if="application" id="approve-form" @submit.prevent="handleSubmit" class="dialog-form">
      <p class="applicant-email"><strong>Email:</strong> {{ application.email }}</p>

      <div class="form-group">
        <label class="form-label">Роль:</label>
        <BaseSelect
          v-model="form.role_id"
          :options="roleOptions"
          placeholder="Выберите роль"
          searchable
        />
      </div>

      <div class="form-group">
        <BaseTextarea
          v-model="form.review_comment"
          label="Комментарий"
          label-position="top"
          placeholder="Комментарий"
          :rows="3"
        />
      </div>
    </form>

    <template #footer>
      <BaseButton variant="outline" @click="emit('update:modelValue', false)"> Отмена </BaseButton>

      <BaseButton
        type="submit"
        form="approve-form"
        variant="primary"
        :disabled="!canSubmit"
        :loading="appStore.isLoading"
      >
        Одобрить
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.applicant-email {
  padding: 12px;
  background: var(--color-background-soft);
  border-radius: 8px;
  color: var(--text-primary);
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
  font: var(--medium-text);
}
</style>
