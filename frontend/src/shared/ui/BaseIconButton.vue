<script setup>
defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value),
  },
  variant: {
    type: String,
    default: 'ghost',
    validator: (value) => ['ghost', 'info', 'danger', 'success'].includes(value),
  },
  label: {
    type: String,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  borderless: {
    type: Boolean,
    default: false,
  },
  withTransform: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['click'])
</script>

<template>
  <button
    type="button"
    class="icon-button"
    :class="[
      `button--${size}`,
      `button--${variant}`,
      {
        'button--borderless': borderless,
        'button--with-transform': withTransform,
      },
    ]"
    :aria-label="label"
    :title="label"
    :disabled="disabled"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<style scoped>
.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid var(--color-border);
  border-radius: 6px;
  background: transparent;
  padding: 0;
  flex-shrink: 0;
  color: var(--text-tertiary);
  opacity: 0.7;
  cursor: pointer;
  transition: all 0.2 ease;
}

.button--small {
  --icon-size: 16px;
  width: 24px;
  height: 24px;
}

.button--medium {
  --icon-size: 18px;
  width: 36px;
  height: 36px;
}

.button--large {
  --icon-size: 22px;
  width: 48px;
  height: 48px;
}

.icon-button :deep(svg) {
  width: var(--icon-size);
  height: var(--icon-size);
}

.icon-button:hover:not(:disabled) {
  opacity: 1;
}

.icon-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.button--with-transform:hover:not(:disabled) {
  transform: translateY(-1px);
}

.button--ghost:hover:not(:disabled) {
  color: var(--secondary);
  border-color: var(--secondary);
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
}

.button--info:hover:not(:disabled) {
  color: var(--info);
  border-color: var(--info);
  background: color-mix(in srgb, var(--info) 10%, transparent);
}

.button--danger:hover:not(:disabled) {
  color: var(--error);
  border-color: var(--error);
  background: color-mix(in srgb, var(--error) 10%, transparent);
}

.button--success:hover:not(:disabled) {
  color: var(--success);
  border-color: var(--success);
  background: color-mix(in srgb, var(--success) 10%, transparent);
}

.button--borderless {
  border: none;
  width: auto;
  height: auto;
  opacity: 1;
}

.button--borderless:hover:not(:disabled) {
  color: var(--text-secondary);
  background: none;
}

.button--borderless :deep(svg) {
  display: block;
  width: auto;
  height: auto;
}
</style>
