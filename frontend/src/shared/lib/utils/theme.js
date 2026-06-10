// Читает CSS-переменную из :root.
export const getCssVar = (name) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

// Все цвета темы для echarts.
export const getThemeColors = () => ({
  // Системные
  primary: getCssVar('--primary'),
  secondary: getCssVar('--secondary'),
  success: getCssVar('--success'),
  warning: getCssVar('--warning'),
  error: getCssVar('--error'),
  info: getCssVar('--info'),

  // Текст и границы
  textPrimary: getCssVar('--text-primary'),
  textSecondary: getCssVar('--text-secondary'),
  textTertiary: getCssVar('--text-tertiary'),
  border: getCssVar('--color-border'),

  // Дашборд: этапы
  stageShe: getCssVar('--chart-stage-she'),
  stageMe: getCssVar('--chart-stage-me'),
  stageRe: getCssVar('--chart-stage-re'),
  stageZe: getCssVar('--chart-stage-ze'),

  // Дашборд: статусы
  statusWinner: getCssVar('--chart-status-winner'),
  statusPrize: getCssVar('--chart-status-prize'),
  statusParticipant: getCssVar('--chart-status-participant'),

  // Дашборд: пол
  genderM: getCssVar('--chart-gender-m'),
  genderF: getCssVar('--chart-gender-f'),

  // Дашборд: графики
  chartYear: getCssVar('--chart-year'),
  chartYearAlt: getCssVar('--chart-year-alt'),
  chartYearSuccess: getCssVar('--chart-year-success'),
  chartSubject: getCssVar('--chart-subject'),
  chartMunicipality: getCssVar('--chart-municipality'),
  chartEducation: getCssVar('--chart-education'),
  chartClass: getCssVar('--chart-class'),
  chartRating: getCssVar('--chart-rating'),
})
