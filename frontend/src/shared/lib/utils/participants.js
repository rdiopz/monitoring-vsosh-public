import { formatDate } from './date'

// Разбирает полное имя на фамилию, имя и отчество
export function parseFullName(fullName) {
  const parts = fullName.trim().split(/\s+/).filter(Boolean)
  return {
    lastname: parts[0] || '',
    firstname: parts[1] || '',
    patronymic: parts[2] || null,
  }
}

// Собирает полное имя из частей
export function buildFullName(lastname, firstname, patronymic) {
  return [lastname, firstname, patronymic].filter(Boolean).join(' ').trim()
}

// Формирует строку для отображения участника в списке поиска
export function participantOptionLabel(participant) {
  const fullName =
    participant.full_name ||
    buildFullName(participant.lastname, participant.firstname, participant.patronymic)
  return `${fullName} (${formatDate(participant.birth_date)})`
}

// Парсит поисковый запрос: извлекает дату рождения и текстовый запрос
export function parseParticipantSearch(query) {
  const dateMatch = query.match(/(\d{2})\.(\d{2})\.(\d{4})/)
  const birthDate = dateMatch ? `${dateMatch[3]}-${dateMatch[2]}-${dateMatch[1]}` : null
  const nameQuery = dateMatch ? query.replace(dateMatch[0], '').trim() : query.trim()
  return { birthDate, nameQuery }
}
