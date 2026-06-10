// Форматирует ISO-дату в локальный формат (ДД.ММ.ГГГГ)
export function formatDate(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('ru-RU')
}

// Форматирует ISO-дату в локальный формат с временем (ДД.ММ.ГГГГ, ЧЧ:ММ:СС)
export function formatDateTime(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('ru-RU')
}

// Форматирует дату в "ДД.ММ.ГГГГ ЧЧ:ММ" (например: 31.12.2025 14:30)
export function formatDateTimeShort(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return (
    date.toLocaleDateString('ru-RU') +
    ' ' +
    date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  )
}

// Форматирует дату в длинный формат (31 декабря 2025 г., 14:30)
export function formatDateTimeLong(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    minute: 'numeric',
    hour: 'numeric',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

// Форматирует дату с возрастом: "ДД.ММ.ГГГГ (N лет)"
export function formatDateWithAge(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  const formatted = date.toLocaleDateString('ru-RU')
  const age = calculateAge(date)
  return `${formatted} (${age})`
}

// Вычисляет возраст по дате рождения
export function calculateAge(birthDate) {
  const today = new Date()
  const date = new Date(birthDate)
  let age = today.getFullYear() - date.getFullYear()
  const monthDifference = today.getMonth() - date.getMonth()
  if (monthDifference < 0 || (monthDifference === 0 && today.getDate() < date.getDate())) {
    age--
  }
  return pluralizeAge(age)
}

// Склоняет слово "год" в зависимости от числа
export function pluralizeAge(age) {
  const absoluteAge = Math.abs(age)
  const lastDigit = absoluteAge % 10
  const lastTwoDigits = absoluteAge % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return `${age} лет`
  if (lastDigit === 1) return `${age} год`
  if (lastDigit >= 2 && lastDigit <= 4) return `${age} года`
  return `${age} лет`
}

// Преобразует дату из ДД.ММ.ГГГГ в ISO-формат YYYY-MM-DD
export function formatToISO(dateString) {
  if (!dateString) return ''
  const parts = dateString.split('.')
  if (parts.length !== 3) return dateString
  const [day, month, year] = parts
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

// Преобразует ISO-дату в строку ДД.ММ.ГГГГ
export function isoToDisplayDate(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}
