import { reactive } from 'vue'

// Создаёт реактивное UI-состояние с методами для URL
export function useUIState(defaults) {
  const ui = reactive({ ...defaults })

  // Только отличающиеся от дефолта поля
  const getUIState = () => {
    const state = {}
    for (const key of Object.keys(ui)) {
      if (JSON.stringify(ui[key]) !== JSON.stringify(defaults[key])) {
        state[key] = JSON.parse(JSON.stringify(ui[key]))
      }
    }
    return state
  }

  // Применить состояние (из URL)
  const setUIState = (state) => Object.assign(ui, state)

  return { ui, getUIState, setUIState }
}
