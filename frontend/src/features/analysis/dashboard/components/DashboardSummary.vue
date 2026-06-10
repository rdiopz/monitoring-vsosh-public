<!--
  Карточки сводных показателей общего дашборда.
  7 карточек: участий, участников, победителей, призёров, предметов, учреждений, муниципалитетов.
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
    { label: 'Уник. участников', value: d.total_participants, color: c.success },
    { label: 'Участий', value: d.total_participations, color: c.chartYear },
    { label: 'Победителей', value: d.total_winners, color: c.statusWinner },
    { label: 'Призёров', value: d.total_prize_winners, color: c.statusPrize },
    { label: 'Предметов', value: d.total_subjects, color: c.chartYear },
    { label: 'Учреждений', value: d.total_educations, color: c.chartEducation },
    { label: 'Муниципалитетов', value: d.total_municipalities, color: c.textSecondary },
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
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 12px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--white);
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.summary-label {
  font: var(--common-text);
  color: var(--text-secondary);
  text-align: center;
}
</style>
