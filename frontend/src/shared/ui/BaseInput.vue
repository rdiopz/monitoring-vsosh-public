<script setup>
import { ref, computed, useSlots } from 'vue'

const slots = useSlots()

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  modelModifiers: {
    type: Object,
    default: () => ({}),
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
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  width: {
    type: String,
    default: '',
  },
  height: {
    type: String,
    default: '',
  },
  borderColor: {
    type: String,
    default: '',
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'tertiary'].includes(value),
  },
  validatePositiveInteger: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'submit'])

const inputRef = ref()

const wrapperStyle = computed(() => {
  const style = {}
  if (props.width) style.width = props.width
  return style
})

const inputStyle = computed(() => {
  const style = {}
  if (props.height) style.height = props.height
  if (props.borderColor) style.borderColor = props.borderColor
  return style
})

const onKeypress = (e) => {
  if (e.key === 'Enter') {
    emit('submit')
  }
}

const focusInput = () => {
  inputRef.value?.focus()
}

// Валидация: разрешаем только цифры (если включено)
const onKeydown = (e) => {
  if (!props.validatePositiveInteger) return

  const allowed = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End']
  if (allowed.includes(e.key) || /^\d$/.test(e.key)) return

  e.preventDefault()
}

const normalizeValue = (value) => {
  if (!props.modelModifiers?.number) return value
  if (value === '') return ''

  const parsed = Number(value)
  return Number.isNaN(parsed) ? value : parsed
}

const onInput = (e) => {
  let value = e.target.value

  if (props.validatePositiveInteger) {
    if (!value || /^\d+$/.test(value)) {
      emit('update:modelValue', normalizeValue(value))
    }
    return
  }

  emit('update:modelValue', normalizeValue(value))
}

const inputClass = computed(() => [
  'input-field',
  `input-field--${props.variant}`,
  { 'input-field--with-prepend': slots.prepend },
  { 'input-field--with-append': slots.append },
])

defineExpose({ focusInput })
</script>

<template>
  <div
    class="input-group"
    :class="[`label--${labelPosition}`, { 'has-error': error }]"
    :style="wrapperStyle"
  >
    <div v-if="label" class="label-wrapper" @click="focusInput">
      <label class="input-label medium-text primary-text">
        <span class="label-text">{{ label }}</span>
        <span v-if="required" class="required-asterisk">*</span>
      </label>
    </div>

    <div class="input-wrapper medium-text primary-text">
      <div class="input-field-wrapper">
        <div v-if="$slots.prepend" class="input-addons input-addons--left">
          <slot name="prepend"></slot>
        </div>

        <input
          ref="inputRef"
          :value="modelValue"
          :required="required"
          :disabled="disabled"
          v-bind="$attrs"
          :style="inputStyle"
          :class="inputClass"
          @keydown="onKeydown"
          @keypress="onKeypress"
          @input="onInput"
          @blur="$emit('blur')"
          @focus="$emit('focus')"
        />

        <div v-if="$slots.append" class="input-addons input-addons--right">
          <slot name="append"></slot>
        </div>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-group {
  display: flex;
  width: 100%;
  min-width: 0;
}

.input-group.label--left {
  flex-direction: row;
  align-items: center;
}

.input-group.label--top {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.label-wrapper {
  flex-shrink: 0;
  cursor: pointer;
}

.input-label {
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

.label--top .input-label {
  width: 100%;
}

.label--left .label-wrapper {
  width: 120px;
}

.label--left .input-label {
  width: 100%;
}

.input-wrapper {
  position: relative;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.input-field-wrapper {
  position: relative;
  width: 100%;
  min-width: 0;
}

.input-addons {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  z-index: 1;
  color: var(--text-tertiary);
}

.input-addons--left {
  left: 12px;
}

.input-addons--right {
  right: 12px;
}

.input-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 16px 14px;
  width: 100%;
  min-width: 0;
  height: 50px;
  border-radius: 8px;
  font: var(--small-text);
  outline: none;
  transition: border-color 0.3s ease;
  background: var(--white);
  color: var(--text-primary);
  box-sizing: border-box;
}

.input-field--primary {
  border: 1.5px solid var(--primary);
}

.input-field--primary:focus {
  border-color: var(--secondary);
}

.input-field--tertiary {
  border: 1.5px solid var(--color-border);
}

.input-field--tertiary:focus {
  border-color: var(--primary);
}

.input-field--tertiary:hover {
  border-color: var(--secondary);
}

.input-field--with-prepend {
  padding-left: 44px;
}

.input-field--with-append {
  padding-right: 44px;
}

.input-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-field::placeholder {
  font: var(--small-text);
  letter-spacing: var(--letter-spacing-normal);
  opacity: 0.7;
  color: var(--text-tertiary);
}

/* Автозаполнение браузера */
.input-field:-webkit-autofill,
.input-field:-webkit-autofill:hover,
.input-field:-webkit-autofill:focus,
.input-field:-webkit-autofill:active {
  -webkit-background-clip: text;
  -webkit-text-fill-color: var(--text-primary);
  transition: background-color 5000s ease-in-out 0s;
  box-shadow: inset 0 0 20px 20px var(--white);
}
/* Убираем стрелочки и делаем текстовым полем, а не числовым для браузеров*/
input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield;
}

input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-group.has-error .input-field {
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
  .input-group.label--left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .label--left .label-wrapper {
    width: 100%;
  }

  .input-wrapper {
    width: 100%;
  }
}
</style>
