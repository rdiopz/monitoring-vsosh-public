<script setup>
import CheckMark from '@icons/actions/CheckMarkIcon.vue'

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'borderless'].includes(value),
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <label
    class="checkbox-wrapper"
    :class="{ 'checkbox-wrapper--borderless': variant === 'borderless' }"
  >
    <input
      :checked="modelValue"
      type="checkbox"
      class="checkbox-input"
      @change="$emit('update:modelValue', $event.target.checked)"
    />
    <span
      class="custom-checkbox"
      :class="{
        'custom-checkbox--borderless': variant === 'borderless',
        checked: modelValue,
      }"
    >
      <CheckMark v-show="modelValue" class="check-icon" />
    </span>
    <span
      v-if="label || $slots.default"
      class="checkbox-label medium-text text-primary"
      v-bind="$attrs"
    >
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<style scoped>
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.checkbox-wrapper--borderless {
  gap: 0;
}

.checkbox-input {
  display: none;
}

.custom-checkbox {
  width: 24px;
  height: 24px;
  background: var(--white);
  border: 1px solid var(--secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.custom-checkbox--borderless {
  width: 18px;
  height: 18px;
  background: transparent;
  border: none;
  border-radius: 0;
}

.check-icon {
  color: var(--secondary);
}

.checkbox-label {
  line-height: 1;
}
</style>
