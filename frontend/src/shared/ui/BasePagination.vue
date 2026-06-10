<script setup>
import { computed, ref, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'
import BaseSelect from './BaseSelect.vue'
import ArrowLeftIcon from '../icons/actions/ArrowLeftIcon.vue'
import DoubleArrowLeftIcon from '../icons/actions/DoubleArrowLeftIcon.vue'
import EllipsisIcon from '../icons/actions/EllipsisIcon.vue'
import ArrowRightIcon from '@icons/actions/ArrowRightIcon.vue'
import DoubleArrowRightIcon from '../icons/actions/DoubleArrowRightIcon.vue'

const props = defineProps({
  modelValue: {
    type: Number,
    required: true,
  },
  totalItems: {
    type: Number,
    default: 0,
  },
  pageSize: {
    type: Number,
    default: 20,
  },
  pageSizeOptions: {
    type: Array,
    default: () => [
      { label: '20', value: 20 },
      { label: '50', value: 50 },
      { label: '100', value: 100 },
      { label: '200', value: 200 },
      { label: '500', value: 500 },
    ],
  },
})

const emit = defineEmits(['update:modelValue', 'update:pageSize'])

const total = computed(() => {
  if (!props.totalItems || !props.pageSize) return 0
  return Math.ceil(props.totalItems / props.pageSize)
})

// Какие страницы показывать
const displayedPages = computed(() => {
  const pages = []
  const totalValue = total.value || 1
  const current = props.modelValue

  // Первая страница всегда
  pages.push(1)

  // Диапазон вокруг текущей
  let start = Math.max(2, current - 2)
  let end = Math.min(totalValue - 1, current + 2)

  // Многоточие после первой страницы
  if (start > 2) {
    pages.push('ellipsis-start')
  }

  // Страницы диапазона
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  // Многоточие перед последней
  if (end < totalValue - 1) {
    pages.push('ellipsis-end')
  }

  // Последняя страница
  if (totalValue > 1) {
    pages.push(totalValue)
  }

  return pages
})

const startIndex = computed(() => {
  return (props.modelValue - 1) * props.pageSize + 1
})

const endIndex = computed(() => {
  const end = props.modelValue * props.pageSize
  return end > props.totalItems ? props.totalItems : end
})

const goToPage = (page) => {
  if (page < 1 || page > total.value) return
  if (page === props.modelValue) return
  emit('update:modelValue', page)
}

const changePage = (delta) => {
  const newPage = props.modelValue + delta
  goToPage(newPage)
}

// Ввод номера страницы с задержкой
const pageDebounceTimer = ref(null)

const onInputPage = (value) => {
  if (pageDebounceTimer.value) {
    clearTimeout(pageDebounceTimer.value)
  }
  pageDebounceTimer.value = setTimeout(() => {
    const page = parseInt(value, 10)
    if (!isNaN(page)) {
      goToPage(page)
    }
    pageDebounceTimer.value = null
  }, 500)
}

const onPageSizeChange = (size) => {
  emit('update:pageSize', size)
}

onUnmounted(() => {
  if (pageDebounceTimer.value) {
    clearTimeout(pageDebounceTimer.value)
  }
})
</script>

<template>
  <div class="pagination">
    <!-- Левая часть: размер страницы + информация -->
    <div class="pagination-left">
      <BaseSelect
        :model-value="pageSize"
        :options="pageSizeOptions"
        @update:model-value="onPageSizeChange"
        position="top"
        :clearable="false"
      />
      <div v-if="totalItems > 0" class="pagination-info">
        Показано с {{ startIndex }} по {{ endIndex }} из {{ totalItems }}
      </div>
    </div>

    <!-- Правая часть: кнопки навигации -->
    <div class="pagination-controls">
      <!-- На первую -->
      <BaseButton
        v-if="total > 1"
        variant="outline"
        :disabled="modelValue === 1"
        @click="goToPage(1)"
        title="На первую страницу"
      >
        <DoubleArrowLeftIcon />
      </BaseButton>

      <!-- На предыдущую -->
      <BaseButton
        v-if="total > 1"
        variant="outline"
        :disabled="modelValue === 1"
        @click="changePage(-1)"
      >
        <ArrowLeftIcon />
      </BaseButton>

      <!-- Номера страниц -->
      <div class="pagination-pages">
        <!-- eslint-disable vue/no-v-for-template-key -->
        <template v-for="page in displayedPages" :key="page">
          <!-- Многоточие -->
          <span
            v-if="page === 'ellipsis-start' || page === 'ellipsis-end'"
            class="pagination-ellipsis"
          >
            <EllipsisIcon />
          </span>

          <!-- Текущая страница — поле ввода -->
          <div v-else-if="page === modelValue" class="pagination-input-wrapper">
            <input
              :value="page"
              type="number"
              class="pagination-input-current"
              @input="onInputPage($event.target.value)"
            />
          </div>

          <!-- Обычная страница — кнопка -->
          <BaseButton
            v-else
            variant="outline"
            size="small"
            class="pagination-page-btn"
            @click="goToPage(page)"
          >
            {{ page }}
          </BaseButton>
        </template>
      </div>

      <!-- На следующую -->
      <BaseButton
        v-if="total > 1"
        variant="outline"
        :disabled="modelValue === total"
        @click="changePage(1)"
      >
        <ArrowRightIcon />
      </BaseButton>

      <!-- На последнюю -->
      <BaseButton
        v-if="total > 1"
        variant="outline"
        size="small"
        :disabled="modelValue === total"
        @click="goToPage(total)"
        title="На последнюю страницу"
      >
        <DoubleArrowRightIcon />
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  width: 100%;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-info {
  color: var(--text-secondary);
  font: var(--small-text);
  white-space: nowrap;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-controls .base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0 !important;
  min-width: 28px;
}

.pagination-controls :deep(svg) {
  width: 14px;
  height: 14px;
  stroke-width: 2;
  stroke: currentColor;
  fill: none;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--secondary);
}

.pagination-ellipsis :deep(svg) {
  width: 18px;
  height: 18px;
}

.pagination-input-wrapper {
  display: inline-flex;
  align-items: center;
}

.pagination-input-current {
  width: 32px;
  height: 28px;
  min-width: 32px;
  text-align: center;
  font-weight: 500;
  padding: 0;
  font-size: var(--font-size-small);
  border-radius: 6px;
  border: 1.5px solid var(--primary);
  background: var(--white);
  color: var(--text-primary);
}

/* Отключаем стрелочки */
.pagination-input-current::-webkit-inner-spin-button,
.pagination-input-current::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.pagination-input-current[type='number'] {
  -moz-appearance: textfield;
  appearance: none;
}

.pagination-page-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-small);
}

@media (max-width: 768px) {
  .pagination {
    flex-wrap: wrap;
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls :deep(svg) {
    width: 12px;
    height: 12px;
  }
}
</style>
