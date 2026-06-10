<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import flatpickr from 'flatpickr'
import 'flatpickr/dist/flatpickr.css'
import { Russian } from 'flatpickr/dist/l10n/ru.js'
import FindIcon from '@icons/actions/FindIcon.vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import { useThemeStore } from '@stores/theme'

defineOptions({
  name: 'BaseDatePicker',
})

const props = defineProps({
  modelValue: {
    type: [String, Array, null],
    default: null,
  },
  mode: {
    type: String,
    default: 'single',
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Выберите дату',
  },
  dateFormat: {
    type: String,
    default: 'd.m.Y H:i:S',
  },
  enableTime: {
    type: Boolean,
    default: true,
  },
  maxDate: {
    type: [String, null],
    default: null,
  },
  minDate: {
    type: [String, null],
    default: null,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  openUp: {
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
})

const datePickerStyle = computed(() => {
  const style = {}
  if (props.width) style.width = props.width
  if (props.height) style.height = props.height
  if (props.borderColor) style.borderColor = props.borderColor
  return style
})

const emit = defineEmits(['update:modelValue', 'onChange'])

const themeStore = useThemeStore()
const inputRef = ref(null)
let fpInstance = null

const clearValue = (event) => {
  event.stopPropagation()

  if (fpInstance) {
    fpInstance.clear()
  }

  emit('update:modelValue', null)
  emit('onChange', null)
}

const initFlatpickr = () => {
  if (!inputRef.value) return

  fpInstance = flatpickr(inputRef.value, {
    mode: props.mode,
    dateFormat: props.dateFormat,
    enableTime: props.enableTime,
    enableSeconds: true,
    time_24hr: true,
    locale: Russian,
    maxDate: props.maxDate,
    minDate: props.minDate,
    disableMobile: true,
    allowInput: true,
    clickOpens: true,
    static: true,
    position: props.openUp ? 'above' : 'auto',
    onClose: (selectedDates, dateStr) => {
      const value = props.mode === 'range' ? selectedDates : dateStr || null
      emit('update:modelValue', value)
      emit('onChange', value)
    },
  })
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (!fpInstance) return

    if (newValue === null || newValue === '') {
      fpInstance.clear()
    } else {
      fpInstance.setDate(newValue, true)
    }
  },
)

watch(
  () => [props.maxDate, props.minDate, props.mode, props.openUp],
  () => {
    if (fpInstance) {
      fpInstance.set('maxDate', props.maxDate)
      fpInstance.set('minDate', props.minDate)
      fpInstance.set('mode', props.mode)
      fpInstance.set('position', props.openUp ? 'above' : 'auto')
    }
  },
)

watch(
  () => themeStore.isDark,
  () => {
    if (fpInstance) {
      fpInstance.destroy()
      setTimeout(initFlatpickr, 0)
    }
  },
)

onMounted(() => {
  initFlatpickr()

  if (props.modelValue && fpInstance) {
    fpInstance.setDate(props.modelValue, true)
  }
})

onUnmounted(() => {
  if (fpInstance) {
    fpInstance.destroy()
  }
})
</script>

<template>
  <div
    class="date-picker"
    :class="{
      'date-picker--disabled': disabled,
      'date-picker--open-up': openUp,
    }"
  >
    <label v-if="label" class="date-picker-label small-text">
      {{ label }}
    </label>

    <div class="date-picker-input-wrapper">
      <input
        ref="inputRef"
        type="text"
        class="date-picker-input"
        :placeholder="placeholder"
        :disabled="disabled"
        :style="datePickerStyle"
      />

      <div class="date-picker-actions">
        <div v-if="clearable && modelValue" class="date-picker-clear" @click="clearValue">
          <ClearIcon class="clear-icon" />
        </div>

        <div class="date-picker-icon">
          <FindIcon class="calendar-icon" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.date-picker {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.date-picker--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.date-picker-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.date-picker-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.date-picker-input-wrapper :deep(.flatpickr-wrapper) {
  flex: 1;
  width: 100%;
}

.date-picker-input {
  flex: 1;
  width: 100%;
  padding: 10px 70px 10px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--white);
  color: var(--text-primary);
  font: var(--small-text);
  cursor: pointer;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.date-picker-input:focus {
  outline: none;
  border-color: var(--primary);
}

.date-picker-actions {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  pointer-events: none;
}

.date-picker-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.date-picker-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: auto;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0.2s ease,
    visibility 0.2s ease;
}

.date-picker-input-wrapper:hover .date-picker-clear {
  opacity: 1;
  visibility: visible;
}

.calendar-icon,
.clear-icon {
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
  display: block;
}

.date-picker-clear:hover .clear-icon {
  color: var(--error);
}

:deep(.flatpickr-calendar) {
  background: var(--color-background) !important;
  border: 1.5px solid var(--color-border) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  border-radius: 8px !important;
  margin: 16px !important;
}

.date-picker--open-up :deep(.flatpickr-calendar.static) {
  top: auto !important;
  bottom: calc(100% + 8px) !important;
  margin: 0 !important;
  z-index: 30 !important;
}

:deep(.flatpickr-months) {
  background: var(--color-background) !important;
}

/* Заголовок календаря (месяц и год) */
:deep(.flatpickr-month) {
  background: var(--color-background) !important;
  color: var(--text-primary) !important;
  fill: var(--text-primary) !important;
}

:deep(.flatpickr-month .flatpickr-month-dropdown) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month select.flatpickr-monthDropdown-month) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month select.flatpickr-monthDropdown-month option) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month select.flatpickr-monthDropdown-year) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month select.flatpickr-monthDropdown-year option) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month .flatpickr-monthDropdown-month) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-month .flatpickr-monthDropdown-year) {
  background: var(--color-background-soft) !important;
  color: var(--text-primary) !important;
}

:deep(.flatpickr-current-month) {
  color: var(--text-primary) !important;
}

:deep(.flatpickr-prev-month),
:deep(.flatpickr-next-month) {
  fill: var(--text-primary) !important;
}

:deep(.flatpickr-prev-month:hover),
:deep(.flatpickr-next-month:hover) {
  fill: var(--primary) !important;
}

:deep(.flatpickr-weekday) {
  color: var(--text-secondary) !important;
  background: var(--color-background) !important;
}

/* Числа: обычный стиль */
:deep(.flatpickr-day) {
  color: var(--text-primary) !important;
  border-color: transparent !important;
}

:deep(.flatpickr-day:hover) {
  background: var(--color-background-soft) !important;
  border-color: var(--color-background-soft) !important;
}

/* Числа: выбранный день */
:deep(.flatpickr-day.selected) {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: var(--white) !important;
}

:deep(.flatpickr-day.selected:hover) {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: var(--white) !important;
}

/* Числа: диапазон (для range mode) */
:deep(.flatpickr-day.inRange) {
  background: var(--color-background-soft) !important;
  border-color: var(--color-background-soft) !important;
}

/* Числа: сегодняшний день */
:deep(.flatpickr-day.today) {
  border-color: var(--primary) !important;
}

:deep(.flatpickr-day.today:hover) {
  background: var(--color-background-soft) !important;
  border-color: var(--primary) !important;
}

/* Числа: неактивные дни */
:deep(.flatpickr-day.flatpickr-disabled) {
  color: var(--text-tertiary) !important;
  cursor: not-allowed;
}

/* Числа: дни предыдущего/следующего месяца */
:deep(.flatpickr-day.prevMonthDay),
:deep(.flatpickr-day.nextMonthDay) {
  color: var(--text-tertiary) !important;
}

/* Блок времени (часы, минуты, секунды) */
:deep(.flatpickr-time) {
  background: var(--color-background) !important;
  border-top: 1px solid var(--color-border) !important;
}

:deep(.flatpickr-time input),
:deep(.flatpickr-time .flatpickr-time-separator) {
  color: var(--text-primary) !important;
  background: var(--color-background-soft) !important;
}

/* Стрелки вверх/вниз для времени */
:deep(.flatpickr-time .numInputWrapper span.arrowUp) {
  border-bottom-color: var(--text-secondary) !important;
}

:deep(.flatpickr-time .numInputWrapper span.arrowDown) {
  border-top-color: var(--text-secondary) !important;
}

/* AM/PM переключатель */
:deep(.flatpickr-time .flatpickr-am-pm) {
  color: var(--text-primary) !important;
  background: var(--color-background-soft) !important;
}

:deep(.flatpickr-time .flatpickr-am-pm:hover),
:deep(.flatpickr-time input:hover) {
  background: var(--color-background-soft) !important;
}

@media (max-width: 768px) {
  .date-picker {
    min-width: 100%;
    width: 100%;
  }

  .date-picker-input {
    padding: 10px 60px 10px 12px;
  }

  .date-picker-actions {
    right: 10px;
  }
}
</style>
