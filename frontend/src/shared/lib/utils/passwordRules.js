// Необходимые правила для создания пароля
export const passwordRules = [
  { test: (p) => p.length >= 8, message: 'Минимум 8 символов' },
  { test: (p) => p.length <= 256, message: 'Максимум 256 символов' },
  {
    test: (p) => /^[A-Za-z0-9~!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+$/.test(p),
    message: 'Только латиница, цифры и спецсимволы',
  },
  { test: (p) => /\d/.test(p), message: 'Добавьте цифру' },
  { test: (p) => /[A-Za-z]/.test(p), message: 'Добавьте букву' },
  { test: (p) => /[a-z]/.test(p), message: 'Добавьте строчную букву' },
  { test: (p) => /[A-Z]/.test(p), message: 'Добавьте заглавную букву' },
  {
    test: (p) => /[~!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(p),
    message: 'Добавьте спецсимвол',
  },
  { test: (p) => !/\s/.test(p), message: 'Без пробелов' },
]

// Проверка по правилам
export function getPasswordErrors(password) {
  if (!password) return []
  return passwordRules.filter((rule) => !rule.test(password)).map((rule) => rule.message)
}
