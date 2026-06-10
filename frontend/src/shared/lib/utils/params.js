// Сериализация параметров запроса
export const serializeParams = (params) => {
  const parts = []
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      value.forEach((v) => parts.push(`${key}=${encodeURIComponent(v)}`))
    } else {
      parts.push(`${key}=${encodeURIComponent(value)}`)
    }
  }
  return parts.join('&')
}
