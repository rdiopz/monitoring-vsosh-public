<!--
  Карточки сводных показателей конкретного участника.
  5 карточек: участий, побед, призовых, предметов, лет участия.
-->
<script setup>
import { computed } from 'vue'
import { getThemeColors } from '@utils/theme'

const props = defineProps({
  data: {
    type: Object,
    default: null,
  },
})

const cards = computed(() => {
  const d = props.data
  if (!d) return []

  const c = getThemeColors()

  return [
    { label: 'Участий', value: d.total_participations, color: c.chartYear },
    { label: 'Побед', value: d.total_winners, color: c.statusWinner },
    { label: 'Призовых', value: d.total_prize_winners, color: c.statusPrize },
    { label: 'Предметов', value: d.total_subjects, color: c.chartSubject },
    { label: 'Лет участия', value: d.total_years, color: c.textSecondary },
  ]
})
</script>

<template>
  <div class="summary">
    <div v-for="card in cards" :key="card.label" class="summary-card">
      <span class="summary-value" :style="{ color: card.color }">
        {{ card.value ?? '—' }}
      </span>
      <span class="summary-label">
        {{ card.label }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 14px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 10px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--white);
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.summary-label {
  font: var(--common-text);
  color: var(--text-secondary);
  text-align: center;
}
</style>
