<script setup>
import BaseDialog from '@ui/BaseDialog.vue'
import BaseButton from '@ui/BaseButton.vue'
defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  entityName: {
    type: String,
    required: true,
  },
  itemName: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const onConfirm = () => {
  emit('confirm')
}

const onCancel = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :title="`Удалить ${entityName}`"
    width="500px"
  >
    <p class="delete-message medium-text text-primary">
      Вы уверены, что хотите удалить {{ entityName }} <strong> {{ itemName }}</strong
      >?
    </p>
    <p class="delete-warning small-text text-error">Это действие нельзя отменить.</p>
    <template #footer>
      <BaseButton type="button" variant="outline" size="medium" @click="onCancel">
        Отмена
      </BaseButton>
      <BaseButton
        type="button"
        variant="primary"
        size="medium"
        :loading="loading"
        @click="onConfirm"
      >
        Удалить
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.delete-message {
  margin: 0 0 16px 0;
}
.delete-warning {
  margin: 0;
  font-weight: 500;
}
</style>
