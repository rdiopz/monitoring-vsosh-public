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
  fingerprint: '',
  user_id: null,
  exclude_jti: false,
})

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.session) {
      form.value = {
        fingerprint: props.session.fingerprint,
        user_id: null,
        exclude_jti: false,
      }
    }
  },
)

const handleConfirm = async () => {
  const payload = {
    fingerprint: form.value.fingerprint,
    user_id: form.value.user_id || undefined,
    exclude_jti: form.value.exclude_jti ? props.session?.jti : undefined,
  }

  const result = await sessionsStore.revokeByFingerprint(payload)

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
    title="Завершить сессии по отпечатку"
    width="500px"
  >
    <form id="revoke-fingerprint-form" @submit.prevent="handleConfirm" class="dialog-form">
      <p class="dialog-description">
        Завершить все сессии с указанным fingerprint? Это затронет всех пользователей.
      </p>

      <div class="form-group">
        <label class="form-label">Fingerprint:</label>
        <BaseInput v-model="form.fingerprint" type="text" readonly />
      </div>

      <div class="form-group">
        <label class="form-label">User ID (необязательно):</label>
        <BaseInput
          v-model="form.user_id"
          type="number"
          placeholder="Ограничить только этим пользователем"
          validate-positive-integer
        />
      </div>

      <BaseCheckBox v-model="form.exclude_jti" label="Исключить выбранную сессию из отзыва" />
    </form>

    <template #footer>
      <BaseButton variant="outline" @click="emit('update:modelValue', false)"> Отмена </BaseButton>

      <BaseButton
        type="submit"
        form="revoke-fingerprint-form"
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
