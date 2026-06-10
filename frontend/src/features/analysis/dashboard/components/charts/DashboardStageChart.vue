<!--
  Столбчатая диаграмма участий по этапам олимпиады.
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

const LABELS = {
  ШЭ: 'Школьный',
  МЭ: 'Муниципальный',
  РЭ: 'Региональный',
  ЗЭ: 'Заключительный',
}

const option = computed(() => {
  const c = getThemeColors()

  const STAGE_COLORS = {
    ШЭ: c.stageShe,
    МЭ: c.stageMe,
    РЭ: c.stageRe,
    ЗЭ: c.stageZe,
  }

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
      data: props.data.map((d) => LABELS[d.stage] ?? d.stage),
      axisLabel: { color: c.textSecondary },
      axisLine: { lineStyle: { color: c.border } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: c.textSecondary },
      splitLine: { lineStyle: { color: c.border } },
    },
    series: [
      {
        name: 'Участий',
        type: 'bar',
        data: props.data.map((d) => ({
          value: d.participations,
          itemStyle: { color: STAGE_COLORS[d.stage] || c.secondary },
        })),
        barMaxWidth: 36,
        borderRadius: [4, 4, 0, 0],
      },
    ],
  }
})
</script>

<template>
  <div class="chart-card">
    <span class="chart-title">Участие по этапам</span>
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
