<template>
  <svg viewBox="0 0 24 24" fill="currentColor" class="ellipsis-icon">
    <circle cx="6" cy="12" r="2" />
    <circle cx="12" cy="12" r="2" />
    <circle cx="18" cy="12" r="2" />
  </svg>
</template>

<style scoped>
.ellipsis-icon circle {
  transition: transform 0.2s ease;
  transform-origin: center;
}
.ellipsis-icon:hover circle {
  transform: scale(1.25);
}
</style>
