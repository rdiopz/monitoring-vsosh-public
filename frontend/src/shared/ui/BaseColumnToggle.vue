<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import CheckMark from '@icons/actions/CheckMarkIcon.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Array,
    default: null,
  },
  position: {
    type: String,
    default: 'bottom',
    validator: (v) => ['top', 'bottom'].includes(v),
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const dropdownRef = ref(null)

const defaultColumns = computed(() =>
  props.columns.filter((c) => c.visible !== false).map((c) => c.key),
)

const visibleColumns = computed({
  get: () => props.modelValue ?? props.columns.map((c) => c.key),
  set: (value) => emit('update:modelValue', value),
})

const isAllVisible = computed(() => visibleColumns.value.length === props.columns.length)

const toggleColumn = (key) => {
  const idx = visibleColumns.value.indexOf(key)
  visibleColumns.value =
    idx === -1 ? [...visibleColumns.value, key] : visibleColumns.value.filter((k) => k !== key)
}

const toggleAll = () => {
  visibleColumns.value = isAllVisible.value ? [] : props.columns.map((c) => c.key)
}

const resetToDefault = () => {
  visibleColumns.value = [...defaultColumns.value]
}

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) isOpen.value = false
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="dropdownRef" class="column-toggle">
    <button class="column-toggle-btn" @click="isOpen = !isOpen">
      <span class="column-toggle-btn-text small-text">Колонки</span>
      <span class="column-toggle-btn-arrow" :class="{ 'column-toggle-btn-arrow--open': isOpen }">
        <ArrowDownIcon />
      </span>
    </button>

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="column-toggle-dropdown"
        :class="{
          'column-toggle-dropdown--bottom': position === 'bottom',
          'column-toggle-dropdown--top': position === 'top',
        }"
      >
        <div class="column-toggle-header">
          <span class="column-toggle-title small-text">Отображаемые колонки</span>
        </div>

        <div class="column-toggle-list">
          <div
            v-for="col in columns"
            :key="col.key"
            class="column-toggle-item"
            :class="{ 'column-toggle-item--checked': visibleColumns.includes(col.key) }"
            @click.stop="toggleColumn(col.key)"
          >
            <span class="column-toggle-item-label">{{ col.label }}</span>
            <CheckMark v-if="visibleColumns.includes(col.key)" class="column-toggle-item-check" />
          </div>
        </div>

        <div class="column-toggle-footer">
          <button class="column-toggle-footer-btn" @click.stop="toggleAll">
            {{ isAllVisible ? 'Снять все' : 'Выбрать все' }}
          </button>
          <button class="column-toggle-footer-btn" @click.stop="resetToDefault">
            По умолчанию
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.column-toggle {
  position: relative;
}

.column-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 44px;
}

.column-toggle-btn:hover {
  border-color: var(--primary);
}

.column-toggle-btn-text {
  color: var(--text-secondary);
}

.column-toggle-btn-arrow {
  display: inline-flex;
  color: var(--text-tertiary);
  transition: transform 0.2s;
}

.column-toggle-btn-arrow--open {
  transform: rotate(180deg);
}

.column-toggle-dropdown {
  position: absolute;
  left: 0;
  min-width: 240px;
  background: var(--white);
  border: 1.5px solid var(--primary);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.column-toggle-dropdown--bottom {
  top: calc(100% + 4px);
}

.column-toggle-dropdown--top {
  bottom: calc(100% + 4px);
}

.column-toggle-header {
  padding: 12px 16px 8px;
}

.column-toggle-title {
  color: var(--text-secondary);
  font-weight: 500;
}

.column-toggle-list {
  overflow-y: auto;
  max-height: 240px;
}

.column-toggle-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.column-toggle-item:hover {
  background: var(--color-background-soft);
}

.column-toggle-item--checked {
  background: color-mix(in srgb, var(--secondary) 6%, transparent);
}

.column-toggle-item-label {
  color: var(--text-primary);
  font: var(--small-text);
  user-select: none;
  flex: 1;
  line-height: 1.4;
}

.column-toggle-item-check {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  color: var(--secondary);
}

.column-toggle-footer {
  display: flex;
  gap: 4px;
  padding: 8px 16px;
  border-top: 1px solid var(--color-border);
}

.column-toggle-footer-btn {
  background: none;
  border: none;
  color: var(--secondary);
  cursor: pointer;
  font: var(--small-text);
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.column-toggle-footer-btn:hover {
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.column-toggle-list::-webkit-scrollbar {
  width: 5px;
}

.column-toggle-list::-webkit-scrollbar-track {
  background: transparent;
}

.column-toggle-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

@media (max-width: 768px) {
  .column-toggle-dropdown {
    left: 0;
    max-width: calc(100vw - 32px);
  }
}
</style>
