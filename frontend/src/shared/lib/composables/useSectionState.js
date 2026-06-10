import { watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import pako from 'pako'

// Сжимает объект в строку для URL
function encodeState(obj) {
  if (Object.keys(obj).length === 0) return ''
  const json = JSON.stringify(obj)
  const compressed = pako.deflate(json, { level: 9 }) // как в ZIP
  const base64 = btoa(String.fromCharCode(...compressed))
  // убираем символы недружелюбные к URL
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

// Разжимает строку из URL обратно в объект
function decodeState(str) {
  if (!str) return {}
  try {
    const base64 = str.replace(/-/g, '+').replace(/_/g, '/')
    const compressed = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0))
    const json = pako.inflate(compressed, { to: 'string' })
    return JSON.parse(json)
  } catch {
    return {} // битый URL
  }
}

// Связывает состояние секции с URL
export function useSectionState(sectionKey, store) {
  const route = useRoute()
  const router = useRouter()

  // Восстанавливаем состояние из URL при загрузке
  onMounted(() => {
    const raw = route.query.state
    if (raw) {
      const allStates = decodeState(raw)
      const myState = allStates[sectionKey]
      if (myState) store.setUIState(myState)
    }
  })

  // Сохраняем состояние в URL при изменении
  watch(
    () => store.ui,
    () => {
      const raw = route.query.state
      const allStates = raw ? decodeState(raw) : {}

      const myState = store.getUIState()
      if (Object.keys(myState).length > 0) {
        allStates[sectionKey] = myState
      } else {
        delete allStates[sectionKey]
      }

      const query = { ...route.query }
      const encoded = encodeState(allStates)
      if (encoded) {
        query.state = encoded
      } else {
        delete query.state
      }

      router.replace({ query })
    },
    { deep: true },
  )
}
