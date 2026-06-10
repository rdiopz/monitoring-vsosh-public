<!--
  Простая таблица всех участий конкретного участника.
-->
<script setup>
import BaseTag from '@ui/BaseTag.vue'

defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})

const STAGE_LABELS = {
  ШЭ: 'Школьный',
  МЭ: 'Муниципальный',
  РЭ: 'Региональный',
  ЗЭ: 'Заключительный',
}

const getStageVariant = (stage) => {
  const map = {
    ШЭ: 'stage-she',
    МЭ: 'stage-me',
    РЭ: 'stage-re',
    ЗЭ: 'stage-ze',
  }
  return map[stage] || 'default'
}

const getStatusVariant = (status) => {
  const map = {
    победитель: 'primary',
    призёр: 'info',
    участник: 'success',
  }
  return map[status] || 'default'
}
</script>

<template>
  <div class="table-card">
    <span class="table-title">Все участия</span>

    <div v-if="data.length" class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>Год</th>
            <th>Этап</th>
            <th>Статус</th>
            <th>Предмет</th>
            <th>Класс</th>
            <th>Учреждение</th>
            <th>Муниципалитет</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.olymp_id">
            <td>{{ row.year }}</td>
            <td>
              <BaseTag
                :label="STAGE_LABELS[row.stage] || row.stage"
                :variant="getStageVariant(row.stage)"
                size="small"
              />
            </td>
            <td>
              <BaseTag :label="row.status" :variant="getStatusVariant(row.status)" size="small" />
            </td>
            <td>{{ row.subject__short_name || row.subject__full_name }}</td>
            <td>{{ row.class_field }}</td>
            <td>{{ row.education__short_name || row.education__full_name }}</td>
            <td>{{ row.education__municipality__name }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="table-empty">Нет данных</p>
  </div>
</template>

<style scoped>
.table-card {
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.table-title {
  font: var(--semibold-head-text);
  color: var(--text-primary);
}

.table-wrapper {
  overflow-x: auto;
  scrollbar-width: thin;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font: var(--common-text);
  color: var(--text-primary);
}

.table th {
  text-align: left;
  padding: 10px 12px;
  font: var(--head-text);
  color: var(--text-secondary);
  background: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.table tr:last-child td {
  border-bottom: none;
}

.table tr:hover td {
  background: var(--color-background-soft);
}

.table-empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  font: var(--common-text);
}
</style>
