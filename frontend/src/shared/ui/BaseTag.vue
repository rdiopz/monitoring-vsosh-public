<script setup>
defineProps({
  label: {
    type: String,
    default: '',
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) =>
      [
        'default',
        'success',
        'warning',
        'error',
        'info',
        'secondary',
        'primary',
        'stage-she',
        'stage-me',
        'stage-re',
        'stage-ze',
      ].includes(value),
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value),
  },
  icon: {
    type: Object,
    default: null,
  },
})
</script>

<template>
  <span class="tag" :class="[`tag--${variant}`, `tag--${size}`]">
    <component v-if="icon" :is="icon" class="tag-icon" />
    <span class="tag-label">{{ label }}</span>
  </span>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 16px;
  font-weight: 500;
  white-space: nowrap;
}

.tag--small {
  padding: 2px 8px;
  font-size: 11px;
}

.tag--medium {
  padding: 4px 12px;
  font-size: 13px;
}

.tag--large {
  padding: 6px 16px;
  font-size: 14px;
}

.tag--default {
  background: color-mix(in srgb, var(--text-tertiary) 15%, transparent);
  color: var(--text-tertiary);
}

.tag--primary {
  background: color-mix(in srgb, var(--primary) 30%, transparent);
  color: var(--primary);
}

.tag--secondary {
  background: color-mix(in srgb, var(--secondary) 30%, transparent);
  color: var(--secondary);
}

.tag--success {
  background: color-mix(in srgb, var(--success) 20%, transparent);
  color: var(--success);
}

.tag--warning {
  background: color-mix(in srgb, var(--warning) 20%, transparent);
  color: var(--warning);
}

.tag--error {
  background: color-mix(in srgb, var(--error) 20%, transparent);
  color: var(--error);
}

.tag--info {
  background: color-mix(in srgb, var(--info) 20%, transparent);
  color: var(--info);
}

.tag--stage-she {
  background: color-mix(in srgb, var(--chart-stage-she) 25%, transparent);
  color: var(--chart-stage-she);
}

.tag--stage-me {
  background: color-mix(in srgb, var(--chart-stage-me) 20%, transparent);
  color: var(--chart-stage-me);
}

.tag--stage-re {
  background: color-mix(in srgb, var(--chart-stage-re) 18%, transparent);
  color: var(--chart-stage-re);
}

.tag--stage-ze {
  background: color-mix(in srgb, var(--chart-stage-ze) 18%, transparent);
  color: var(--chart-stage-ze);
}

.tag-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.tag--small .tag-icon {
  width: 12px;
  height: 12px;
}

.tag--large .tag-icon {
  width: 16px;
  height: 16px;
}
</style>
