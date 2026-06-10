<script setup>
defineProps({
  size: {
    type: String,
    default: '40px',
  },
  variant: {
    type: String,
    default: 'secondary',
    validator: (value) => ['primary', 'secondary'].includes(value),
  },
  text: {
    type: String,
    default: 'Загрузка...',
  },
})
</script>

<template>
  <div class="spinner">
    <div
      class="spinner-circle"
      :class="[`spinner-circle--${variant}`]"
      :style="{
        width: size,
        height: size,
      }"
    ></div>
    <p v-if="text" class="spinner-text medium-text text-tertiary">{{ text }}</p>
  </div>
</template>

<style scoped>
.spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner-circle {
  margin-bottom: 16px;
  border: 3px solid var(--color-border);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-circle--primary {
  border-top-color: var(--primary);
}

.spinner-circle--secondary {
  border-top-color: var(--secondary);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
