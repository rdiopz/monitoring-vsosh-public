<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import FindIcon from '@icons/actions/FindIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'
import BaseSpinner from '@ui/BaseSpinner.vue'
import EmptyState from '@ui/EmptyState.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, null],
    default: null,
  },
  options: {
    type: Array,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Выберите значение',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  searchable: {
    type: Boolean,
    default: false,
  },
  position: {
    type: String,
    default: 'bottom',
    validator: (value) => ['top', 'bottom'].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  maxHeight: {
    type: String,
    default: '320px',
  },
  inputMode: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'search', 'focus', 'blur', 'scroll-end'])

const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref(null)
const searchTimeout = ref(null)
const isInternalSearchUpdate = ref(false)
const scrollEndTriggered = ref(false)

const SCROLL_END_THRESHOLD = 24

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue)
})

const selectedLabel = computed(() => {
  return selectedOption.value?.label || props.placeholder
})

const hasValue = computed(() => {
  return props.modelValue !== null && props.modelValue !== undefined
})

const showDropdownSearch = computed(() => {
  return props.searchable && !props.inputMode
})

const showInitialLoader = computed(() => {
  return props.loading && filteredOptions.value.length === 0
})

const showBottomLoader = computed(() => {
  return props.loading && filteredOptions.value.length > 0
})

// Локальную фильтрацию используем только в обычном режиме
const filteredOptions = computed(() => {
  if (!props.searchable || props.inputMode || !searchQuery.value) {
    return props.options
  }

  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return props.options

  return props.options.filter((opt) => String(opt.label).toLowerCase().includes(query))
})

// Обновляем текст без лишнего emit('search')
const setSearchQuerySilently = (value) => {
  isInternalSearchUpdate.value = true
  searchQuery.value = value

  nextTick(() => {
    isInternalSearchUpdate.value = false
  })
}

const resetScrollEndState = () => {
  scrollEndTriggered.value = false
}

const closeDropdown = () => {
  if (!isOpen.value) return

  isOpen.value = false
  resetScrollEndState()

  if (!props.inputMode) {
    setSearchQuerySilently('')
  }
}

const openDropdown = () => {
  if (props.disabled) return

  if (!props.inputMode) {
    setSearchQuerySilently('')
  }

  isOpen.value = true
  resetScrollEndState()
}

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value ? closeDropdown() : openDropdown()
}

// Поиск отправляем с debounce.
watch(searchQuery, (newQuery) => {
  if (!props.searchable || isInternalSearchUpdate.value) return

  clearTimeout(searchTimeout.value)

  searchTimeout.value = setTimeout(() => {
    emit('search', newQuery)
    resetScrollEndState()
  }, 300)
})

// В inputMode подтягиваем label выбранной опции
watch(
  () => [props.modelValue, props.options],
  ([val, opts]) => {
    if (!props.inputMode) return
    if (val === null || val === undefined || val === '') return

    const option = opts.find((opt) => opt.value === val)
    if (option) {
      setSearchQuerySilently(option.label)
    }
  },
  { flush: 'post', immediate: true },
)

watch(
  () => props.loading,
  () => {
    if (!props.loading) {
      resetScrollEndState()
    }
  },
)

watch(
  () => props.options,
  () => {
    resetScrollEndState()
  },
)

const selectFirstOption = () => {
  if (filteredOptions.value.length > 0) {
    selectOption(filteredOptions.value[0])
  }
}

const onInputKeydown = (event) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    selectFirstOption()
  }

  if (event.key === 'Escape') {
    closeDropdown()
  }
}

const selectOption = (option) => {
  emit('update:modelValue', option.value)
  emit('change', option)

  if (props.inputMode) {
    setSearchQuerySilently(option.label)
  }

  closeDropdown()
}

// В inputMode после clear оставляем dropdown открытым.
const clearValue = (event) => {
  event.stopPropagation()

  emit('update:modelValue', null)
  emit('change', null)

  if (props.inputMode) {
    setSearchQuerySilently('')
    resetScrollEndState()

    if (!isOpen.value) {
      isOpen.value = true
    }

    emit('search', '')
    return
  }

  closeDropdown()
}

const clearSearch = () => {
  setSearchQuerySilently('')
  emit('search', '')
  resetScrollEndState()
}

const handleClickOutside = (event) => {
  if (!isOpen.value) return

  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
    emit('blur')
  }
}

const handleFocus = () => {
  emit('focus')
  openDropdown()
}

const handleBlur = () => {
  emit('blur')
}

// Когда доходим до низа, просим родителя догрузить данные.
const handleOptionsScroll = (event) => {
  if (props.loading) return

  const el = event.target
  if (!el) return

  const isNearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - SCROLL_END_THRESHOLD

  if (isNearBottom) {
    if (!scrollEndTriggered.value) {
      scrollEndTriggered.value = true
      emit('scroll-end')
    }
  } else {
    scrollEndTriggered.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  clearTimeout(searchTimeout.value)
})
</script>

<template>
  <div ref="dropdownRef" class="select" :class="{ 'select--disabled': disabled }">
    <label v-if="label" class="select-label small-text">{{ label }}</label>

    <template v-if="inputMode">
      <div
        class="select-trigger select-trigger--input"
        :class="{
          'select-trigger--open': isOpen,
          'select-trigger--open-top': isOpen && position === 'top',
        }"
      >
        <FindIcon class="search-icon-trigger" />

        <input
          v-model="searchQuery"
          type="text"
          class="select-trigger-input"
          :placeholder="selectedOption ? selectedOption.label : placeholder"
          :disabled="disabled"
          @click="openDropdown"
          @focus="handleFocus"
          @blur="handleBlur"
          @keyup.esc="closeDropdown"
          @keydown.enter="onInputKeydown"
        />

        <button
          v-if="clearable && hasValue"
          class="select-clear"
          type="button"
          title="Очистить"
          @click.stop="clearValue"
        >
          <ClearIcon class="clear-icon" />
        </button>

        <div v-else class="select-arrow">
          <ArrowDownIcon />
        </div>
      </div>
    </template>

    <template v-else>
      <div
        class="select-trigger"
        :class="{
          'select-trigger--open': isOpen,
          'select-trigger--open-top': isOpen && position === 'top',
        }"
        @click="toggleDropdown"
      >
        <div class="select-value" :title="selectedLabel">
          <span :class="{ 'select-value--placeholder': !hasValue }">
            {{ selectedLabel }}
          </span>
        </div>

        <button
          v-if="clearable && hasValue"
          class="select-clear"
          type="button"
          title="Очистить"
          @click.stop="clearValue"
        >
          <ClearIcon class="clear-icon" />
        </button>

        <div v-else class="select-arrow">
          <ArrowDownIcon />
        </div>
      </div>
    </template>

    <div
      v-if="isOpen"
      class="select-dropdown"
      :class="{
        'select-dropdown--bottom': position === 'bottom',
        'select-dropdown--top': position === 'top',
      }"
    >
      <div v-if="showDropdownSearch" class="select-search">
        <FindIcon class="search-icon" />

        <input
          v-model="searchQuery"
          type="text"
          class="select-search-input"
          placeholder="Поиск..."
          @click.stop
          @focus="emit('focus')"
          @blur="handleBlur"
          @keyup.esc="closeDropdown"
          @keydown.enter="onInputKeydown"
        />

        <button
          v-if="searchQuery && !loading"
          class="select-search-clear"
          type="button"
          @click.stop="clearSearch"
        >
          <ClearIcon class="clear-icon" />
        </button>
      </div>

      <div class="select-options" @scroll.passive="handleOptionsScroll">
        <template v-if="showInitialLoader">
          <div class="select-loader">
            <BaseSpinner text="Загрузка..." />
          </div>
        </template>

        <template v-else-if="filteredOptions.length === 0">
          <EmptyState message="Ничего не найдено" />
        </template>

        <template v-else>
          <div
            v-for="option in filteredOptions"
            :key="option.value"
            class="select-option"
            :class="{ 'select-option--selected': option.value === modelValue }"
            @click.stop="selectOption(option)"
          >
            <span class="select-option-label" :title="option.label">
              {{ option.label }}
            </span>
          </div>

          <div v-if="showBottomLoader" class="select-bottom-loader">
            <BaseSpinner text="Загрузка..." />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.select {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  min-width: 0;
}

.select--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.select-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.select-trigger {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 44px;
  padding: 10px 40px 10px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  color: var(--text-primary);
  font: var(--small-text);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.select-trigger:hover {
  border-color: var(--primary);
}

.select-trigger--open:not(.select-trigger--open-top) {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.select-trigger--open-top {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.select-trigger--input {
  padding: 10px 40px 10px 12px;
  gap: 8px;
}

.search-icon-trigger {
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.select-trigger-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font: var(--small-text);
  color: var(--text-primary);
  padding: 0;
}

.select-value {
  flex: 1;
  min-width: 0;
}

.select-value span {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.select-value--placeholder {
  color: var(--text-tertiary);
}

.select-arrow,
.select-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  transition: transform 0.2s ease;
}

.select-trigger--open .select-arrow,
.select-trigger--open-top .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

.select-clear {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.select-clear:hover {
  background: var(--color-background-soft);
  color: var(--error);
}

.select-dropdown {
  position: absolute;
  left: 0;
  width: 100%;
  background: var(--white);
  border: 1.5px solid var(--primary);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.select-dropdown--bottom {
  top: 100%;
  margin-top: -1px;
  border-top: none;
  border-radius: 0 0 8px 8px;
}

.select-dropdown--top {
  bottom: 100%;
  margin-bottom: -5px;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
}

.select-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
}

.search-icon,
.clear-icon {
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.select-search-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font: var(--small-text);
  color: var(--text-primary);
}

.select-search-clear {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.select-options {
  overflow-y: auto;
  max-height: v-bind(maxHeight);
  padding: 4px 0;
}

.select-loader {
  padding: 16px 12px;
}

.select-bottom-loader {
  padding: 10px 12px 14px;
  border-top: 1px solid color-mix(in srgb, var(--color-border) 60%, transparent);
}

.select-option {
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 60%, transparent);
}

.select-option:last-child {
  border-bottom: none;
}

.select-option:hover {
  background: var(--color-background-soft);
}

.select-option--selected {
  background: color-mix(in srgb, var(--secondary) 12%, transparent);
}

.select-option-label {
  display: block;
  color: var(--text-primary);
  font: var(--small-text);
  line-height: 1.35;
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
}
</style>
