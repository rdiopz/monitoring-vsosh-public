<!--
  Круговая диаграмма: распределение статусов участника.
-->
<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getThemeColors } from '@utils/theme'

use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})

const option = computed(() => {
  const c = getThemeColors()

  const STATUS_COLORS = {
    победитель: c.statusWinner,
    призёр: c.statusPrize,
    участник: c.statusParticipant,
  }

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      bottom: 0,
      textStyle: { color: c.textSecondary },
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          color: c.textSecondary,
        },
        data: props.data.map((d) => ({
          name: d.status,
          value: d.count,
          itemStyle: {
            color: STATUS_COLORS[d.status] || c.textTertiary,
          },
        })),
      },
    ],
  }
})
</script>

<template>
  <div class="chart-card">
    <span class="chart-title">Статусы участника</span>
    <VChart v-if="data.length" class="chart-body" :option="option" autoresize />
    <p v-else class="chart-empty">Нет данных</p>
  </div>
</template>

<style scoped>
.chart-card {
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 320px;
}

.chart-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
}

.chart-body {
  flex: 1;
  min-height: 260px;
}

.chart-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font: var(--common-text);
}
</style>
