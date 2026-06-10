import { decodeMimeString } from '@utils/mime'

// Скачивает файл из ответа API и показывает тост.
export function downloadFile(response, defaultFilename, toast) {
  // Расшифровываем имя файла из заголовка
  const rawHeader = response.headers['content-disposition']
  const decodedHeader = decodeMimeString(rawHeader)
  const match = decodedHeader.match(/filename="?([^"]+)"?/)
  const filename = match?.[1] ? decodeURIComponent(match[1]) : defaultFilename

  // Скачивание
  const url = URL.createObjectURL(new Blob([response.data]))
  const link = Object.assign(document.createElement('a'), { href: url, download: filename })
  link.click()
  URL.revokeObjectURL(url)

  // Тост с сообщением от сервера
  const rawMessage = response.headers['x-message']
  if (rawMessage) toast.success(decodeMimeString(rawMessage))
}
