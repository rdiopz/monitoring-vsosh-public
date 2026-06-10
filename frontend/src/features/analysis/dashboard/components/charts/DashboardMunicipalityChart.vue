<!--
  Горизонтальная столбчатая диаграмма: участие по муниципалитетам.
-->
<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getThemeColors } from '@utils/theme'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})

const option = computed(() => {
  const c = getThemeColors()

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: {
      top: 10,
      bottom: 10,
      left: 16,
      right: 40,
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: c.textSecondary },
      splitLine: { lineStyle: { color: c.border } },
    },
    yAxis: {
      type: 'category',
      data: props.data.map((d) => d.education__municipality__name).reverse(),
      axisLabel: {
        width: 160,
        overflow: 'truncate',
        color: c.textSecondary,
      },
      axisLine: { lineStyle: { color: c.border } },
    },
    series: [
      {
        type: 'bar',
        data: [...props.data.map((d) => d.participations)].reverse(),
        color: c.chartMunicipality,
        barMaxWidth: 20,
        borderRadius: [0, 4, 4, 0],
      },
    ],
  }
})
</script>

<template>
  <div class="chart-card">
    <span class="chart-title">Участие по муниципалитетам</span>
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
  min-height: 400px;
}

.chart-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
}

.chart-body {
  flex: 1;
  min-height: 340px;
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
