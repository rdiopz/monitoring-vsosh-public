<script setup>
import { computed } from 'vue'

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const activeTab = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})
</script>

<template>
  <div class="base-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="tabs-button"
      :class="{ 'tabs-button--active': activeTab === tab.value }"
      @click="activeTab = tab.value"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.base-tabs {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 0;
  gap: 30px;
  width: 100%;
  height: auto;
  background: transparent;
}

.tabs-button {
  display: flex;
  flex-direction: column;
  padding: 8px 31px 14px;
  height: auto;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--secondary);
  font: var(--medium-text);
  position: relative;
  transition: all 0.3 ease;
}

.tabs-button::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: var(--secondary);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.tabs-button--active::after {
  width: 100%;
}

.tabs-button--active {
  font-weight: 700;
}

.tabs-button:hover:not(.tabs-button--active) {
  background: color-mix(in srgb, var(--secondary) 5%, transparent);
}
</style>
