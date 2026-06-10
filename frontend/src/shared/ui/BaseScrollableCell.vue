<script setup>
defineProps({
  text: {
    type: String,
    default: '',
  },
  maxWidth: {
    type: String,
    default: '200px',
  },
  maxHeight: {
    type: String,
    default: '80px',
  },
  nowrap: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div
    class="scrollable-cell"
    :class="{ 'scrollable-cell--nowrap': nowrap }"
    :style="{ maxWidth: maxWidth, maxHeight: maxHeight }"
    :title="text || ''"
  >
    {{ text || '—' }}
  </div>
</template>

<style scoped>
.scrollable-cell {
  display: block;
  overflow: auto;
  scrollbar-width: thin;
  color: var(--text-primary);
}

.scrollable-cell--nowrap {
  white-space: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
}
</style>
