<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import FindIcon from '@icons/actions/FindIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'
import CheckMark from '@icons/actions/CheckMarkIcon.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  options: {
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Выберите значения',
  },
  label: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  width: {
    type: String,
    default: '',
  },
  height: {
    type: String,
    default: '',
  },
  borderColor: {
    type: String,
    default: '',
  },
  dropdownWidth: {
    type: String,
    default: '',
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  position: {
    type: String,
    default: 'bottom',
    validator: (v) => ['top', 'bottom'].includes(v),
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref(null)
const triggerRef = ref(null)
const hoveredOption = ref(null)

const triggerStyle = computed(() => {
  const style = {}
  if (props.width) style.width = props.width
  if (props.height) style.height = props.height
  if (props.borderColor) style.borderColor = props.borderColor
  return style
})

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) return props.options
  const query = searchQuery.value.toLowerCase()
  return props.options.filter((option) => option.label.toLowerCase().includes(query))
})

const selectedCount = computed(() => props.modelValue.length)

const selectedLabels = computed(() => {
  const selected = props.options
    .filter((o) => props.modelValue.includes(o.value))
    .map((o) => o.label)

  return selected.length ? selected.join(', ') : props.placeholder
})

const isAllSelected = computed(() => {
  return props.options.length > 0 && props.modelValue.length === props.options.length
})

// Если dropdownWidth не задан — дропдаун сам растянется через CSS (width: 100%)
const dropdownStyle = computed(() => {
  if (!props.dropdownWidth) return {}

  const minW = triggerRef.value?.offsetWidth || 0

  return {
    width: props.dropdownWidth,
    minWidth: `${minW}px`,
  }
})

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
  hoveredOption.value = null
}

const openDropdown = () => {
  if (props.disabled) return
  searchQuery.value = ''
  isOpen.value = true
}

const toggleDropdown = () => {
  isOpen.value ? closeDropdown() : openDropdown()
}

const toggleAll = () => {
  const next = isAllSelected.value ? [] : props.options.map((o) => o.value)
  emit('update:modelValue', next)
  emit('change', next)
}

const toggleOption = (val) => {
  const next = props.modelValue.includes(val)
    ? props.modelValue.filter((v) => v !== val)
    : [...props.modelValue, val]

  emit('update:modelValue', next)
  emit('change', next)
}

const selectOnly = (val) => {
  emit('update:modelValue', [val])
  emit('change', [val])
}

const selectExcept = (val) => {
  const next = props.options.filter((o) => o.value !== val).map((o) => o.value)

  emit('update:modelValue', next)
  emit('change', next)
}

const clearSearch = () => {
  searchQuery.value = ''
}

const handleClickOutside = (e) => {
  if (!isOpen.value) return

  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    closeDropdown()
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="dropdownRef" class="multi-select" :class="{ 'multi-select--disabled': disabled }">
    <label v-if="label" class="multi-select-label small-text">
      {{ label }}
    </label>

    <div
      ref="triggerRef"
      class="multi-select-trigger"
      :class="{ 'multi-select-trigger--open': isOpen }"
      :style="triggerStyle"
      @click="toggleDropdown"
    >
      <div
        class="multi-select-value"
        :class="{ 'multi-select-value--placeholder': selectedCount === 0 }"
      >
        <span class="multi-select-value-text">{{ selectedLabels }}</span>
      </div>

      <span v-if="selectedCount > 0" class="multi-select-count">
        {{ selectedCount }}
      </span>

      <span class="multi-select-arrow">
        <ArrowDownIcon />
      </span>
    </div>

    <div
      v-if="isOpen"
      class="multi-select-dropdown"
      :class="{
        'multi-select-dropdown--bottom': position === 'bottom',
        'multi-select-dropdown--top': position === 'top',
      }"
      :style="dropdownStyle"
    >
      <div class="multi-select-search">
        <template v-if="searchable">
          <FindIcon class="multi-select-search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            class="multi-select-search-input"
            placeholder="Поиск..."
            @click.stop
            @keyup.esc="closeDropdown"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="multi-select-search-clear"
            @click.stop="clearSearch"
          >
            <ClearIcon class="multi-select-clear-icon" />
          </button>
        </template>

        <button type="button" class="multi-select-select-all-btn" @click.stop="toggleAll">
          {{ isAllSelected ? 'Сбросить' : 'Выбрать всё' }}
        </button>
      </div>

      <div class="multi-select-options">
        <div
          v-for="option in filteredOptions"
          :key="option.value"
          class="multi-select-option"
          :class="{
            'multi-select-option--selected': modelValue.includes(option.value),
            'multi-select-option--out-of-filter': option.outOfFilter,
          }"
          @mouseenter="hoveredOption = option.value"
          @mouseleave="hoveredOption = null"
          @click.stop="toggleOption(option.value)"
        >
          <span class="multi-select-label-text">{{ option.label }}</span>

          <!-- Галочка или только/кроме — всегда на одном месте справа -->
          <span class="multi-select-right-slot">
            <CheckMark
              class="multi-select-check-mark"
              :class="{
                // Галочку прячем при наведении или если опция не выбрана
                'multi-select-check-mark--hidden':
                  hoveredOption === option.value || !modelValue.includes(option.value),
              }"
            />
            <span v-if="hoveredOption === option.value" class="multi-select-action-btn">
              <button
                v-if="!(modelValue.length === 1 && modelValue.includes(option.value))"
                type="button"
                @click.stop="selectOnly(option.value)"
              >
                Только
              </button>
              <button v-else type="button" @click.stop="selectExcept(option.value)">Кроме</button>
            </span>
          </span>
        </div>

        <div v-if="filteredOptions.length === 0" class="multi-select-empty">Ничего не найдено</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-select {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  min-width: 0;
}

.multi-select--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.multi-select-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.multi-select-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-width: 0;
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 44px;
  box-sizing: border-box;
}

.multi-select-trigger:hover {
  border-color: var(--primary);
}

.multi-select-trigger--open {
  border-color: var(--primary);
}

.multi-select-value {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.multi-select-value-text {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font: var(--small-text);
  color: var(--text-primary);
}

.multi-select-value--placeholder .multi-select-value-text {
  color: var(--text-tertiary);
}

.multi-select-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  background: var(--secondary);
  color: var(--white);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  border-radius: 11px;
  flex-shrink: 0;
}

.multi-select-arrow {
  display: inline-flex;
  color: var(--text-tertiary);
  transition: transform 0.2s;
  flex-shrink: 0;
}

.multi-select-trigger--open .multi-select-arrow {
  transform: rotate(180deg);
}

.multi-select-dropdown {
  position: absolute;
  left: 0;
  width: 100%;
  min-width: 0;
  background: var(--white);
  border: 1.5px solid var(--primary);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.multi-select-dropdown--bottom {
  top: calc(100% + 4px);
}

.multi-select-dropdown--top {
  bottom: calc(100% + 4px);
}

.multi-select-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  background: var(--white);
  min-width: 0;
}

.multi-select-search-icon,
.multi-select-clear-icon {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.multi-select-search-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font: var(--small-text);
  color: var(--text-primary);
}

.multi-select-search-clear {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  flex-shrink: 0;
}

.multi-select-search-clear:hover {
  background: var(--color-border);
}

.multi-select-select-all-btn {
  background: none;
  border: none;
  color: var(--secondary);
  cursor: pointer;
  font: var(--small-text);
  padding: 2px 4px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.multi-select-select-all-btn:hover {
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
}

.multi-select-options {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  max-height: 280px;
}

.multi-select-option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.multi-select-option:hover {
  background: var(--color-background-soft);
}

.multi-select-option--selected {
  background: color-mix(in srgb, var(--secondary) 6%, transparent);
}

.multi-select-option--out-of-filter .multi-select-label-text {
  color: var(--text-tertiary);
  font-style: italic;
}

.multi-select-label-text {
  color: var(--text-primary);
  font: var(--small-text);
  user-select: none;
  flex: 1;
  min-width: 0;
  line-height: 1.5;
  word-break: break-word;
}

.multi-select-right-slot {
  position: relative;
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  margin-top: 2px;
}

.multi-select-check-mark {
  position: absolute;
  right: 0;
  top: 0;
  width: 16px;
  height: 16px;
  color: var(--secondary);
}

.multi-select-check-mark--hidden {
  opacity: 0;
}

.multi-select-action-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
}

.multi-select-action-btn button {
  background: var(--color-background-soft);
  border: none;
  color: var(--secondary);
  cursor: pointer;
  font: var(--small-text);
  padding: 1px 6px;
  border-radius: 4px;
}

.multi-select-action-btn button:hover {
  text-decoration: underline;
}

.multi-select-empty {
  padding: 16px;
  text-align: center;
  color: var(--text-tertiary);
  font: var(--small-text);
}

.multi-select-options::-webkit-scrollbar {
  width: 5px;
}

.multi-select-options::-webkit-scrollbar-track {
  background: transparent;
}

.multi-select-options::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

@media (max-width: 768px) {
  .multi-select {
    width: 100%;
    min-width: 0;
  }

  .multi-select-search {
    flex-wrap: wrap;
    align-items: center;
  }

  .multi-select-search-input {
    min-width: 120px;
  }

  .multi-select-select-all-btn {
    margin-left: auto;
  }
}
</style>
