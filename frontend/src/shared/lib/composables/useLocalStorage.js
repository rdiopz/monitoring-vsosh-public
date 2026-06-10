import { ref, watch } from 'vue'

/**
 * Сохраняет и читает данные из localStorage.
 * @param {string} key - уникальное наименование
 * @param {*} defaultValue - значение по умолчанию
 * @param {object} options - методы для получения и сохранения данных
 * @returns {import('vue').Ref} данные, которыми можно управлять
 */
export function useLocalStorage(key, defaultValue, options = {}) {
  const { deep = false, serializer = JSON.stringify, deserializer = JSON.parse } = options

  const getStoredValue = () => {
    const stored = localStorage.getItem(key)
    if (stored === null) return defaultValue

    try {
      return deserializer(stored)
    } catch {
      return defaultValue
    }
  }
  const data = ref(getStoredValue())

  watch(
    data,
    (newValue) => {
      const serialized = serializer(newValue)
      localStorage.setItem(key, serialized)
    },
    { deep },
  )

  return data
}

// Заготовки для использования разных типов данных
export function useLocalStorageBoolean(key, defaultValue = false) {
  return useLocalStorage(key, defaultValue, {
    serializer: (value) => String(value),
    deserializer: (value) => value === 'true',
  })
}

export function useLocalStorageNumber(key, defaultValue = 0) {
  return useLocalStorage(key, defaultValue, {
    serializer: (value) => String(value),
    deserializer: (value) => Number(value),
  })
}

export function useLocalStorageObject(key, defaultValue = {}) {
  return useLocalStorage(key, defaultValue, {
    deep: true,
  })
}

export function useLocalStorageArray(key, defaultValue = []) {
  return useLocalStorage(key, defaultValue, {
    deep: true,
  })
}
