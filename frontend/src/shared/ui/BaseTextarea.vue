<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  labelPosition: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'top'].includes(value),
  },
  placeholder: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  rows: {
    type: Number,
    default: 3,
  },
  width: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const wrapperStyle = computed(() => {
  const style = {}
  if (props.width) style.width = props.width
  return style
})

const onInput = (e) => {
  emit('update:modelValue', e.target.value)
}
</script>

<template>
  <div
    class="textarea-group"
    :class="[`label--${labelPosition}`, { 'has-error': error }]"
    :style="wrapperStyle"
  >
    <div v-if="label" class="label-wrapper">
      <label class="textarea-label medium-text primary-text">
        <span class="label-text">{{ label }}</span>
        <span v-if="required" class="required-asterisk">*</span>
      </label>
    </div>

    <div class="textarea-wrapper">
      <textarea
        :value="modelValue"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :rows="rows"
        class="textarea-field"
        @input="onInput"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      ></textarea>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.textarea-group {
  display: flex;
}

.textarea-group.label--left {
  flex-direction: row;
  align-items: flex-start;
}

.textarea-group.label--top {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.label-wrapper {
  flex-shrink: 0;
  cursor: pointer;
}

.textarea-label {
  display: inline-block;
  color: var(--text-primary);
  line-height: 1.4;
}

.label-text {
  word-break: break-word;
  white-space: normal;
  text-align: left;
}

.required-asterisk {
  color: var(--error);
  margin-left: 1px;
}

.label--top .label-wrapper {
  width: 100%;
}

.label--top .textarea-label {
  width: 100%;
}

.label--left .label-wrapper {
  width: 120px;
  padding-top: 12px;
}

.label--left .textarea-label {
  width: 100%;
}

.textarea-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.textarea-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 12px 14px;
  width: 100%;
  min-width: 120px;
  min-height: 50px;
  border-radius: 8px;
  font: var(--small-text);
  outline: none;
  transition: border-color 0.3s ease;
  background: var(--white);
  color: var(--text-primary);
  border: 1.5px solid var(--color-border);
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}

.textarea-field:focus {
  border-color: var(--primary);
}

.textarea-field:hover {
  border-color: var(--secondary);
}

.textarea-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.textarea-field::placeholder {
  font: var(--small-text);
  letter-spacing: var(--letter-spacing-normal);
  opacity: 0.7;
  color: var(--text-tertiary);
}

.textarea-group.has-error .textarea-field {
  border-color: var(--error);
}

.error-message {
  margin-top: 4px;
  font: var(--small-text);
  color: var(--error);
  font-size: 14px;
  min-height: 16px;
  word-wrap: break-word;
}

@media (max-width: 768px) {
  .textarea-group.label--left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .label--left .label-wrapper {
    width: 100%;
    padding-top: 0;
  }

  .textarea-wrapper {
    width: 100%;
  }
}
</style>
