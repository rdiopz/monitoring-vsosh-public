<!--
  Столбчатая диаграмма участий конкретного участника по годам.
  Три серии: участий, побед, призовых.
-->
<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getThemeColors } from '@utils/theme'

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})

const option = computed(() => {
  const c = getThemeColors()

  return {
    tooltip: { trigger: 'axis' },
    legend: {
      bottom: 0,
      textStyle: { color: c.textSecondary },
    },
    grid: {
      top: 20,
      bottom: 48,
      left: 16,
      right: 16,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.data.map((d) => String(d.year)),
      axisLabel: { color: c.textSecondary },
      axisLine: { lineStyle: { color: c.border } },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: c.textSecondary },
      splitLine: { lineStyle: { color: c.border } },
    },
    series: [
      {
        name: 'Участий',
        type: 'bar',
        data: props.data.map((d) => d.participations),
        color: c.chartYear,
        barMaxWidth: 36,
        borderRadius: [4, 4, 0, 0],
      },
      {
        name: 'Побед',
        type: 'bar',
        data: props.data.map((d) => d.winners),
        color: c.statusWinner,
        barMaxWidth: 36,
        borderRadius: [4, 4, 0, 0],
      },
      {
        name: 'Призовых',
        type: 'bar',
        data: props.data.map((d) => d.prize_winners),
        color: c.statusPrize,
        barMaxWidth: 36,
        borderRadius: [4, 4, 0, 0],
      },
    ],
  }
})
</script>

<template>
  <div class="chart-card">
    <span class="chart-title">Участия по годам</span>
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
