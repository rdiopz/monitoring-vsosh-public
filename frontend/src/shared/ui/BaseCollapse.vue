<script setup>
import { ref, computed, watch } from 'vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  openTitle: {
    type: String,
    default: '',
  },
  defaultOpen: {
    type: Boolean,
    default: false,
  },
  modelValue: {
    type: Boolean,
    default: undefined,
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(props.modelValue ?? props.defaultOpen)

watch(
  () => props.modelValue,
  (val) => {
    if (val !== undefined) isOpen.value = val
  },
)

const toggle = () => {
  isOpen.value = !isOpen.value
  emit('update:modelValue', isOpen.value)
}

const currentTitle = computed(() => {
  if (props.openTitle && isOpen.value) return props.openTitle
  return props.title
})
</script>

<template>
  <div class="collapse" :class="{ 'collapse--closed': !isOpen }">
    <div
      class="collapse-header"
      :class="{ 'collapse-header--open': isOpen }"
      :title="isOpen ? 'Свернуть' : 'Развернуть'"
      @click="toggle"
    >
      <span class="collapse-title medium-text text-primary">{{ currentTitle }}</span>
      <BaseIconButton
        variant="ghost"
        borderless
        size="small"
        :label="isOpen ? 'Свернуть' : 'Развернуть'"
        class="collapse-icon"
        :class="{ 'collapse-icon--open': isOpen }"
      >
        <ArrowDownIcon />
      </BaseIconButton>
    </div>

    <Transition name="collapse-fade">
      <div v-show="isOpen" class="collapse-content">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.collapse {
  margin-bottom: 30px;
  border: 2px solid var(--color-border);
  border-radius: 12px;
}

.collapse--closed {
  overflow: hidden;
}

.collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--color-background-soft);
  cursor: pointer;
  transition: background 0.2s ease;
  border-radius: 10px;
}

.collapse-header--open {
  border-radius: 10px 10px 0 0;
}

.collapse-header:hover {
  background: var(--color-background-mute);
}

.collapse-title {
  margin: 0;
}

.collapse-icon {
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  transform: rotate(180deg);
  pointer-events: none;
}

.collapse-icon--open {
  transform: rotate(0deg);
}

.collapse-content {
  padding: 24px;
  border-top: 1px solid var(--color-border);
}

.collapse-fade-enter-active,
.collapse-fade-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-fade-enter-from,
.collapse-fade-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.collapse-fade-enter-to,
.collapse-fade-leave-from {
  opacity: 1;
  max-height: 2000px;
}
</style>
