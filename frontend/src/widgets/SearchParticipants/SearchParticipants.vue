<script setup>
import { ref, watch } from 'vue'
import { useParticipantsStore } from '@entities/participants'
import { participantOptionLabel } from '@utils/participants'

import BaseSelect from '@ui/BaseSelect.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  placeholder: {
    type: String,
    default: 'ФИО или дата рождения...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  maxHeight: {
    type: String,
    default: '360px',
  },
  initialOption: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'selected'])

const participantsStore = useParticipantsStore()

const options = ref([])
const searchQuery = ref('')
const searchOffset = ref(0)
const searchHasMore = ref(false)

const SEARCH_LIMIT = 20

const mapResultsToOptions = (results) =>
  results.map((participant) => ({
    label: participantOptionLabel(participant),
    value: Number(participant.participant_id),
    data: participant,
  }))

// Объединяем опции без дублей по value.
const mergeUniqueOptions = (current, incoming) => {
  const map = new Map()

  current.forEach((item) => {
    map.set(item.value, item)
  })

  incoming.forEach((item) => {
    map.set(item.value, item)
  })

  return Array.from(map.values())
}

// Загружаем участников по query и limit/offset.
const loadOptions = async ({ query = '', offset = 0, append = false } = {}) => {
  const response = await participantsStore.searchParticipants({
    q: query,
    limit: SEARCH_LIMIT,
    offset,
  })

  const nextOptions = mapResultsToOptions(response.results || [])

  options.value = append ? mergeUniqueOptions(options.value, nextOptions) : nextOptions

  searchOffset.value = response.next_offset ?? 0
  searchHasMore.value = Boolean(response.has_more)
}

// Новый поиск всегда начинается с offset = 0.
const handleSearch = async (query) => {
  searchQuery.value = query || ''
  searchOffset.value = 0
  searchHasMore.value = false

  try {
    await loadOptions({
      query: searchQuery.value,
      offset: 0,
      append: false,
    })
  } catch (error) {
    console.error('Ошибка поиска участников:', error)
  }
}

// При открытии показываем последние записи.
const handleFocus = async () => {
  if (options.value.length > 0) return

  try {
    await loadOptions({
      query: '',
      offset: 0,
      append: false,
    })
  } catch (error) {
    console.error('Ошибка загрузки участников:', error)
  }
}

// Догружаем следующую порцию при скролле вниз.
const handleScrollEnd = async () => {
  if (participantsStore.isSearching || !searchHasMore.value) return

  try {
    await loadOptions({
      query: searchQuery.value,
      offset: searchOffset.value,
      append: true,
    })
  } catch (error) {
    console.error('Ошибка догрузки участников:', error)
  }
}

// Отдаём наружу и value, и объект участника.
const handleUpdateModelValue = (value) => {
  emit('update:modelValue', value)

  if (value === null || value === undefined || value === '') {
    emit('selected', null)
    return
  }

  const found = options.value.find((option) => option.value === value)
  emit('selected', found?.data ?? null)
}

// Подмешиваем текущую выбранную опцию, чтобы она не пропала из селекта.
watch(
  () => props.initialOption,
  (option) => {
    if (!option) return
    options.value = mergeUniqueOptions([option], options.value)
  },
  { immediate: true },
)
</script>

<template>
  <BaseSelect
    :model-value="modelValue"
    :options="options"
    :placeholder="placeholder"
    :disabled="disabled"
    :clearable="clearable"
    :loading="participantsStore.isSearching"
    :searchable="true"
    :input-mode="true"
    :max-height="maxHeight"
    @update:model-value="handleUpdateModelValue"
    @search="handleSearch"
    @focus="handleFocus"
    @scroll-end="handleScrollEnd"
  />
</template>
