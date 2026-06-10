<script setup>
import { ref, watch } from 'vue'
import { useSessionsStore } from '@entities/sessions'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import BaseDialog from '@ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  session: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'revoked'])

const sessionsStore = useSessionsStore()

const form = ref({
  user_id: null,
  exclude_current: false,
})

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.session) {
      form.value = {
        user_id: props.session.user_id,
        exclude_current: false,
      }
    }
  },
)

const handleConfirm = async () => {
  const payload = {
    user_id: form.value.user_id,
    exclude_jti: form.value.exclude_current ? props.session?.jti : undefined,
  }

  const result = await sessionsStore.revokeAllUserSessions(payload)

  if (result.success) {
    emit('update:modelValue', false)
    emit('revoked')
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Завершить все сессии пользователя"
    width="500px"
  >
    <form id="revoke-sessions-form" @submit.prevent="handleConfirm" class="dialog-form">
      <p class="dialog-description">
        Завершить все сессии указанного пользователя? Пользователь будет разлогинен со всех
        устройств.
      </p>

      <div class="form-group">
        <label class="form-label">User ID:</label>
        <BaseInput v-model="form.user_id" type="number" readonly />
      </div>

      <BaseCheckBox v-model="form.exclude_current" label="Исключить выбранную сессию из отзыва" />
    </form>

    <template #footer>
      <BaseButton variant="outline" @click="emit('update:modelValue', false)"> Отмена </BaseButton>

      <BaseButton
        type="submit"
        form="revoke-sessions-form"
        variant="primary"
        :loading="sessionsStore.isLoading"
      >
        Завершить все
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

.dialog-description {
  color: var(--text-secondary);
  font: var(--small-text);
  line-height: 1.5;
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
