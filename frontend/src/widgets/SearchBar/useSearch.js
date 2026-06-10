import { onUnmounted } from 'vue'

export function useSearch({ onSearch, timeout = 500 } = {}) {
  let searchTimeoutId = null

  onUnmounted(() => {
    clearTimeout(searchTimeoutId)
  })

  const scheduleSearch = (value) => {
    clearTimeout(searchTimeoutId)
    searchTimeoutId = setTimeout(() => {
      onSearch?.(value)
    }, timeout)
  }

  const immediateSearch = (value) => {
    clearTimeout(searchTimeoutId)
    onSearch?.(value)
  }

  return {
    scheduleSearch,
    immediateSearch,
  }
}
