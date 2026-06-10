<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: '',
  },
  value: {
    type: [String, Number, Boolean],
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])

const isChecked = computed(() => props.modelValue === props.value)
</script>

<template>
  <label class="radio-wrapper">
    <input
      :checked="isChecked"
      :value="value"
      type="radio"
      class="radio-input"
      @change="$emit('update:modelValue', value)"
    />
    <span class="custom-radio" :class="{ checked: isChecked }">
      <span v-if="isChecked" class="radio-dot"></span>
    </span>
    <span class="radio-label medium-text text-primary">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<style scoped>
.radio-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.radio-input {
  display: none;
}

.custom-radio {
  width: 20px;
  height: 20px;
  background: var(--white);
  border: 2px solid var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.custom-radio.checked {
  border-color: var(--primary);
}

.radio-dot {
  width: 8px;
  height: 8px;
  background: var(--primary);
  border-radius: 50%;
  transition: all 0.3s ease;
}
</style>
