<script setup>
import { ref, watch, computed } from 'vue'
import { useApplicationsStore } from '@/entities/applications'
import BaseButton from '@ui/BaseButton.vue'
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
})

const emit = defineEmits(['update:modelValue', 'rejected'])

const appStore = useApplicationsStore()

const comment = ref('')

const canSubmit = computed(() => Boolean(comment.value.trim()))

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      comment.value = ''
    }
  },
)

const handleSubmit = async () => {
  if (!canSubmit.value) return

  const result = await appStore.rejectApplication(props.application.application_id, comment.value)

  if (result.success) {
    emit('update:modelValue', false)
    emit('rejected')
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Отклонение заявки"
    width="500px"
    :close-on-backdrop="false"
  >
    <form v-if="application" id="reject-form" @submit.prevent="handleSubmit" class="dialog-form">
      <p class="applicant-email"><strong>Email:</strong> {{ application.email }}</p>

      <BaseTextarea
        v-model="comment"
        label="Причина отклонения"
        label-position="top"
        placeholder="Укажите причину отклонения"
        :rows="3"
        required
      />
    </form>

    <template #footer>
      <BaseButton variant="outline" @click="emit('update:modelValue', false)"> Отмена </BaseButton>

      <BaseButton
        type="submit"
        form="reject-form"
        variant="primary"
        :disabled="!canSubmit"
        :loading="appStore.isLoading"
      >
        Отклонить
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
</style>
