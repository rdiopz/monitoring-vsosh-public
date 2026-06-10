<script setup>
import { ref, nextTick, watch, computed } from 'vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  width: {
    type: String,
    default: '500px',
  },
  height: {
    type: String,
    default: '',
  },
  showClose: {
    type: Boolean,
    default: true,
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'close'])

const dialogRef = ref(null)

const dialogStyle = computed(() => {
  const style = { width: props.width }
  if (props.height) {
    style.minHeight = props.height
  }
  return style
})

const handleClose = () => {
  emit('update:modelValue', false)
  emit('close')
}
// Если есть пропс, то можем закрыть при клике вне диалога
const handleBackdropClick = (event) => {
  if (props.closeOnBackdrop && event.target === dialogRef.value) {
    handleClose()
  }
}

const handleEsc = (event) => {
  if (event.key === 'Escape') {
    handleClose()
  }
}

watch(
  () => props.modelValue,
  async (val) => {
    if (val) {
      await nextTick()
      dialogRef.value?.focus()
    }
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="modelValue"
        ref="dialogRef"
        class="dialog-overlay"
        @click="handleBackdropClick"
        @keydown="handleEsc"
        tabindex="-1"
      >
        <div class="dialog-container" :style="dialogStyle">
          <div v-if="title || showClose" class="dialog-header">
            <h3 v-if="title" class="dialog-title">{{ title }}</h3>
            <BaseIconButton
              v-if="showClose"
              variant="ghost"
              size="medium"
              label="Закрыть"
              borderless
              @click="handleClose"
            >
              <ClearIcon />
            </BaseIconButton>
          </div>

          <div class="dialog-content">
            <slot></slot>
          </div>

          <div v-if="$slots.footer" class="dialog-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
  outline: none;
}

.dialog-container {
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.dialog-title {
  margin: 0;
  font: var(--large-text);
  color: var(--text-primary);
}

.dialog-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
  background: var(--color-background-soft);
}

.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-active .dialog-container,
.dialog-leave-active .dialog-container {
  transition: transform 0.3s ease;
}

.dialog-enter-from .dialog-container,
.dialog-leave-to .dialog-container {
  transform: scale(0.95) translateY(-10px);
}

@media (max-width: 768px) {
  .dialog-container {
    width: 100% !important;
    max-height: 95vh;
  }

  .dialog-header,
  .dialog-content,
  .dialog-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
