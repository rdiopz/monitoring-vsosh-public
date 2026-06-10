// Функция для декодирования MIME-заголовков
export const decodeMimeString = (str) => {
  if (!str) return ''
  const match = str.match(/=\?([^?]+)\?[bB]\?([^?]+)\?=/)
  if (!match) return str

  const text = atob(match[2])
  const bytes = new Uint8Array(text.length)
  for (let i = 0; i < text.length; i++) bytes[i] = text.charCodeAt(i)
  return new TextDecoder(match[1]).decode(bytes)
}
