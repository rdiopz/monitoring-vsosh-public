<template>
  <svg width="24" height="24" viewBox="0 0 24 24" :fill="color">
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M11.4697 14.5303C11.7626 14.8232 12.2374 14.8232 12.5303 14.5303L18.5303 8.53033C18.8232 8.23744 18.8232 7.76256 18.5303 7.46967C18.2374 7.17678 17.7626 7.17678 17.4697 7.46967L12 12.9393L6.53033 7.46967C6.23744 7.17678 5.76256 7.17678 5.46967 7.46967C5.17678 7.76256 5.17678 8.23744 5.46967 8.53033L11.4697 14.5303Z"
    />
  </svg>
</template>

<script setup>
defineProps({
  color: {
    type: String,
    default: 'currentColor',
  },
})
</script>
