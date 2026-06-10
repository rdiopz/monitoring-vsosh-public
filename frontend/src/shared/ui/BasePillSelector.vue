<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const select = (option) => {
  emit('update:modelValue', option.value)
}

const isActive = (option) => {
  return props.modelValue === option.value
}

const pillStyle = (option) => {
  if (option.color && isActive(option)) {
    return { '--pill-color': option.color }
  }
  return {}
}
</script>

<template>
  <div class="pill-selector">
    <label v-if="label" class="pill-label">{{ label }}</label>

    <div class="pill-group">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="pill-btn"
        :class="{ 'pill-btn--active': isActive(option) }"
        :style="pillStyle(option)"
        @click="select(option)"
      >
        {{ option.value }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.pill-selector {
  width: 100%;
  min-width: 0;
  flex-shrink: 0;
}

.pill-label {
  display: block;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
  margin-bottom: 5px;
}

.pill-group {
  display: flex;
  gap: 2px;
  min-height: 42px;
  width: 100%;
  min-width: 0;
}

.pill-btn {
  flex: 1 1 0;
  min-width: 0;
  padding: 0 8px;
  border: 1.5px solid var(--color-border);
  background: var(--white);
  color: var(--text-tertiary);
  font-weight: 500;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 42px;
}

.pill-btn:first-child {
  border-radius: 6px 0 0 6px;
}

.pill-btn:last-child {
  border-radius: 0 6px 6px 0;
}

.pill-btn--active {
  border-color: var(--pill-color, var(--secondary));
  background: color-mix(in srgb, var(--pill-color, var(--secondary)) 15%, transparent);
  color: var(--pill-color, var(--secondary));
  font-weight: 600;
}

.pill-btn:not(.pill-btn--active):hover {
  background: var(--color-background-soft);
  color: var(--text-primary);
}

@media (max-width: 640px) {
  .pill-group {
    flex-wrap: wrap;
    gap: 8px;
    height: auto;
  }

  .pill-btn {
    flex: 1 1 120px;
    border-radius: 6px;
    white-space: normal;
    padding: 10px 12px;
  }

  .pill-btn:first-child,
  .pill-btn:last-child {
    border-radius: 6px;
  }
}
</style>
