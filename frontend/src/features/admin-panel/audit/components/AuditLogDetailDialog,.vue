<script setup>
import { formatDateTime } from '@utils/date'
import BaseDialog from '@ui/BaseDialog.vue'

defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  log: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const parseJSON = (str) => {
  if (!str) return null
  try {
    return typeof str === 'string' ? JSON.parse(str) : str
  } catch {
    return str
  }
}

const formatJSONBlock = (value) => {
  if (!value) return '—'

  const parsed = parseJSON(value)

  if (typeof parsed === 'string') {
    return parsed
  }

  try {
    return JSON.stringify(parsed, null, 2)
  } catch {
    return String(parsed)
  }
}
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="Детали лога аудита"
    width="700px"
  >
    <div v-if="log" class="detail-dialog">
      <div class="detail-row">
        <span class="detail-label">ID:</span>
        <span class="detail-value">{{ log.log_id }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">Время:</span>
        <span class="detail-value">
          {{ formatDateTime(log.timestamp) }}
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">Пользователь:</span>
        <span class="detail-value">{{ log.user_email || '—' }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">Действие:</span>
        <span class="detail-value">{{ log.action || '—' }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">Объект:</span>
        <span class="detail-value">
          {{ log.model_name || '—' }} (ID: {{ log.object_id || '—' }})
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">IP адрес:</span>
        <span class="detail-value">{{ log.ip_address || '—' }}</span>
      </div>

      <div class="detail-section">
        <span class="detail-section-title">Данные запроса</span>
        <pre class="detail-json">{{ formatJSONBlock(log.request_data) }}</pre>
      </div>

      <div v-if="log.old_values" class="detail-section">
        <span class="detail-section-title">Старые значения</span>
        <pre class="detail-json">{{ formatJSONBlock(log.old_values) }}</pre>
      </div>

      <div v-if="log.new_values" class="detail-section">
        <span class="detail-section-title">Новые значения</span>
        <pre class="detail-json">{{ formatJSONBlock(log.new_values) }}</pre>
      </div>
    </div>
  </BaseDialog>
</template>

<style scoped>
.detail-dialog {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-label {
  min-width: 140px;
  font: var(--medium-text);
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-value {
  flex: 1;
  color: var(--text-primary);
  font: var(--small-text);
  word-break: break-word;
}

.detail-section {
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.detail-section-title {
  display: block;
  margin-bottom: 12px;
  font: var(--medium-text);
  color: var(--text-primary);
  font-weight: 500;
}

.detail-json {
  margin: 0;
  padding: 12px;
  background: var(--color-background-mute);
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 300px;
}

@media (max-width: 768px) {
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .detail-label {
    min-width: 0;
  }
}
</style>
