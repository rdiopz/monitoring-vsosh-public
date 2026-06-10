<script setup>
import { computed, ref } from 'vue'
import BaseButton from '@ui/BaseButton.vue'
import CopyIcon from '@icons/actions/CopyIcon.vue'

const props = defineProps({
  variants: {
    type: Array,
    required: true,
  },
})

const copiedIndex = ref(null)

// Для вставки в Excel
const normalizedVariants = computed(() =>
  props.variants.map((v) => ({
    ...v,
    copyText: v.copyText.replace(/, /g, '\t'),
  })),
)

const copyHeaders = async (text, index) => {
  await navigator.clipboard.writeText(text)
  copiedIndex.value = index
  setTimeout(() => {
    copiedIndex.value = null
  }, 1500)
}
</script>

<template>
  <div class="headers-list">
    <div v-for="(variant, index) in normalizedVariants" :key="index" class="headers-row">
      <div class="headers-text">
        <strong>{{ variant.label }}: </strong>
        <span v-for="(header, i) in variant.headers" :key="i">
          <span class="header-item">{{ header }}</span
          ><span v-if="i < variant.headers.length - 1">, </span>
        </span>
      </div>
      <BaseButton variant="ghost" size="small" @click="copyHeaders(variant.copyText, index)">
        <template #icon-left>
          <CopyIcon />
        </template>
        {{ copiedIndex === index ? 'Скопировано' : 'Копировать' }}
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.headers-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.headers-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 16px;
  background: var(--white);
  border: 1px dashed var(--color-border);
  border-radius: 5px;
  line-height: 1.8;
}

.headers-text {
  flex: 1;
  font: var(--small-text);
  color: var(--text-secondary);
}

.headers-text strong {
  color: var(--text-primary);
}

.header-item {
  line-height: 1.8;
  white-space: nowrap;
  color: var(--text-secondary);
}
</style>
