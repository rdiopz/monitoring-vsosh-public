<script setup>
import { computed, ref, watch } from 'vue'
import ClearIcon from '@icons/actions/ClearIcon.vue'
import FindIcon from '@icons/actions/FindIcon.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseIconButton from '@ui/BaseIconButton.vue'
import { useSearch } from './useSearch'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Поиск...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  timeout: {
    type: Number,
    default: 500,
  },
})

const emit = defineEmits(['update:modelValue', 'search'])

const searchQuery = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const { scheduleSearch, immediateSearch } = useSearch({
  onSearch: (value) => {
    emit('search', value)
  },
  timeout: props.timeout,
})

watch(searchQuery, (value) => {
  scheduleSearch(value)
})

const hasValue = computed(() => searchQuery.value.trim().length > 0)
const inputRef = ref(null)
const focusSearchInput = () => inputRef.value?.focusInput()

const clearSearch = () => {
  searchQuery.value = ''
  focusSearchInput()
}

const submitSearch = () => {
  immediateSearch(searchQuery.value)
}
</script>

<template>
  <div class="search-bar">
    <BaseInput
      ref="inputRef"
      v-model="searchQuery"
      :placeholder="placeholder"
      :disabled="disabled"
      variant="tertiary"
      @submit="submitSearch"
    >
      <template #prepend>
        <FindIcon class="search-icon" aria-label="Поиск" title="Поиск" @click="focusSearchInput" />
      </template>

      <template v-if="hasValue" #append>
        <BaseIconButton
          variant="ghost"
          borderless
          size="small"
          label="Очистить текст"
          @click="clearSearch"
        >
          <ClearIcon />
        </BaseIconButton>
      </template>
    </BaseInput>
  </div>
</template>

<style scoped>
.search-bar {
  flex: 1;
  min-width: 150px;
}

.search-icon {
  color: var(--text-tertiary);
}
</style>
