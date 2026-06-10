<script setup>
defineProps({
  message: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="empty-state">
    <span>{{ message }}</span>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}
</style>
