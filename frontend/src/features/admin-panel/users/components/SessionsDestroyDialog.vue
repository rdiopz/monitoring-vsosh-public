<script setup>
import { useSessionsStore } from '@entities/sessions'
import BaseButton from '@ui/BaseButton.vue'
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

const emit = defineEmits(['update:modelValue', 'destroyed'])

const sessionsStore = useSessionsStore()

const handleConfirm = async () => {
  if (!props.session) return

  await sessionsStore.adminDestroySession(props.session.jti)
  emit('update:modelValue', false)
  emit('destroyed')
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Завершить сессию"
    width="500px"
  >
    <div class="dialog-body">
      <p class="dialog-text">Вы уверены, что хотите завершить эту сессию?</p>
      <p class="dialog-note">Пользователь будет разлогинен.</p>

      <div v-if="session" class="session-info">
        <p><strong>Email:</strong> {{ session.user_email || 'Unknown' }}</p>
        <p><strong>JTI:</strong> {{ session.jti?.slice(0, 8) + '...' }}</p>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="outline" @click="emit('update:modelValue', false)"> Отмена </BaseButton>

      <BaseButton variant="primary" :loading="sessionsStore.isLoading" @click="handleConfirm">
        Завершить
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-text {
  color: var(--text-primary);
  margin: 0;
}

.dialog-note {
  padding: 12px;
  background: var(--color-background-soft);
  border-radius: 8px;
  font: var(--tiny-text);
  color: var(--text-secondary);
  margin: 0;
}

.session-info {
  padding: 12px;
  background: var(--color-background-soft);
  border-radius: 8px;
  font: var(--small-text);
}

.session-info p {
  margin: 4px 0;
}

.session-info p:first-child {
  margin-top: 0;
}

.session-info p:last-child {
  margin-bottom: 0;
}
</style>
