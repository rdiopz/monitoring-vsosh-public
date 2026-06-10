<script setup>
defineProps({
  type: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'submit', 'reset'].includes(value),
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'ghost'].includes(value),
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'compact', 'medium', 'large'].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
    validator: (value) => value.length <= 50,
  },
  fullWidth: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['click'])
</script>

<template>
  <button
    :type="type"
    :disabled="loading || disabled"
    :class="[
      'base-button',
      `button--${variant}`,
      `button--${size}`,
      {
        'button--loading': loading,
        'button--full-width': fullWidth,
      },
    ]"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="button-loading">
      <span class="loading-dot"></span>
      <span class="loading-dot"></span>
      <span class="loading-dot"></span>
    </span>

    <template v-else>
      <div v-if="$slots['icon-left']" class="icon-container">
        <slot name="icon-left"></slot>
      </div>

      <span class="button-content">
        <slot>{{ label }}</slot>
      </span>

      <div v-if="$slots['icon-right']" class="icon-container">
        <slot name="icon-right"></slot>
      </div>
    </template>
  </button>
</template>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font: var(--small-text);
  transition: all 0.3s ease;
  flex-shrink: 0;
  min-width: 0;
  max-width: 100%;
}

.button-content {
  display: flex;
  align-items: center;
  min-width: 0;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--btn-icon-size);
  height: var(--btn-icon-size);
  flex-shrink: 0;
}

.icon-container :deep(svg) {
  width: var(--btn-icon-size);
  height: var(--btn-icon-size);
  display: block;
}

.button--primary {
  background: var(--primary);
  color: var(--white);
}

.button--primary:hover:not(:disabled) {
  background: var(--button-hover);
  transform: translateY(-1px);
}

.button--secondary {
  background: var(--white);
  color: var(--text-secondary);
  border: 1px solid var(--color-border);
}

.button--secondary:hover:not(:disabled) {
  border-color: var(--secondary);
  color: var(--secondary);
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
}

.button--outline {
  background: transparent;
  color: var(--primary);
  border: 1.5px solid var(--primary);
}

.button--outline:hover:not(:disabled) {
  background: var(--primary);
  color: var(--white);
}

.button--ghost {
  background: transparent;
  color: var(--text-secondary);
  padding-left: 8px;
  padding-right: 8px;
}

.button--ghost:hover:not(:disabled) {
  background: var(--color-background-soft);
  color: var(--text-primary);
}

.button--small {
  --btn-icon-size: 14px;
  padding: 8px 16px;
  height: 32px;
  font-size: 14px;
}

.button--compact {
  --btn-icon-size: 18px;
  padding: 10px 14px;
  height: 50px;
}

.button--medium {
  --btn-icon-size: 24px;
  padding: 12px 24px;
  height: 40px;
}

.button--large {
  --btn-icon-size: 24px;
  padding: 14px 28px;
  height: 50px;
}

.button--full-width {
  width: 100%;
}

.base-button:disabled {
  background: var(--button-pressed);
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.button-loading {
  display: flex;
  gap: 4px;
  cursor: wait;
}

.loading-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
