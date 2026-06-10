<script setup>
import { computed } from 'vue'
import BaseButton from '@ui/BaseButton.vue'
import ArrowDownIcon from '@icons/actions/ArrowDownIcon.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  extended: {
    type: Boolean,
    default: false,
  },
  // side — кнопки справа
  // stacked — фильтры сверху, кнопки снизу
  // inline — без "Применить", только "Сбросить" и "Фильтры"
  layout: {
    type: String,
    default: 'side',
    validator: (v) => ['side', 'stacked', 'inline'].includes(v),
  },
  columns: {
    type: Number,
    default: 12,
  },
})

const emit = defineEmits(['apply', 'reset', 'update:extended'])

const showExtended = computed({
  get: () => props.extended,
  set: (val) => emit('update:extended', val),
})

const isStacked = computed(() => props.layout === 'stacked')
const isInline = computed(() => props.layout === 'inline')

const gridColumns = computed(() => `repeat(${props.columns}, minmax(0, 1fr))`)
</script>

<template>
  <div class="filters-panel">
    <!-- stacked / inline -->
    <template v-if="isStacked || isInline">
      <div class="filters-body">
        <div
          class="filters-primary"
          :class="{ 'filters-primary--with-extended': $slots.extended && showExtended }"
          :style="{ gridTemplateColumns: gridColumns }"
        >
          <slot name="primary" />
        </div>

        <div
          v-if="$slots.extended && showExtended"
          class="filters-extended filters-extended--stacked"
          :style="{ gridTemplateColumns: gridColumns }"
        >
          <slot name="extended" />
        </div>
      </div>

      <div class="filters-actions filters-actions--stacked">
        <!-- "Применить" только для stacked -->
        <BaseButton
          v-if="isStacked"
          variant="primary"
          size="small"
          :loading="loading"
          @click="emit('apply')"
        >
          Применить
        </BaseButton>

        <BaseButton variant="outline" size="small" @click="emit('reset')"> Сбросить </BaseButton>

        <BaseButton
          v-if="$slots.extended"
          :title="showExtended ? 'Скрыть фильтры' : 'Показать все фильтры'"
          variant="ghost"
          size="small"
          @click="showExtended = !showExtended"
        >
          <template #icon-right>
            <ArrowDownIcon
              class="filters-toggle-icon"
              :class="{ 'filters-toggle-icon--open': showExtended }"
            />
          </template>
          Фильтры
        </BaseButton>
      </div>
    </template>

    <!-- side -->
    <template v-else>
      <div class="filters-row">
        <div class="filters-primary" :style="{ gridTemplateColumns: gridColumns }">
          <slot name="primary" />
        </div>

        <div class="filters-actions">
          <BaseButton variant="primary" size="small" :loading="loading" @click="emit('apply')">
            Применить
          </BaseButton>

          <BaseButton variant="outline" size="small" @click="emit('reset')"> Сбросить </BaseButton>

          <BaseButton
            v-if="$slots.extended"
            :title="showExtended ? 'Скрыть фильтры' : 'Показать все фильтры'"
            variant="ghost"
            size="small"
            @click="showExtended = !showExtended"
          >
            <template #icon-right>
              <ArrowDownIcon
                class="filters-toggle-icon"
                :class="{ 'filters-toggle-icon--open': showExtended }"
              />
            </template>
            Фильтры
          </BaseButton>
        </div>
      </div>

      <div
        v-if="$slots.extended && showExtended"
        class="filters-extended"
        :style="{ gridTemplateColumns: gridColumns }"
      >
        <slot name="extended" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.filters-panel {
  position: relative;
  isolation: isolate;
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: visible;
  z-index: 10;
}

.filters-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--white);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  pointer-events: none;
  z-index: -1;
}

.filters-row,
.filters-body,
.filters-extended {
  position: relative;
}

.filters-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px 16px;
  align-items: end;
  padding: 16px;
  z-index: 2;
}

.filters-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 16px;
  z-index: 2;
}

.filters-primary {
  display: grid;
  gap: 12px 14px;
  min-width: 0;
}

.filters-primary--with-extended {
  padding-bottom: 14px;
}

.filters-primary > * {
  min-width: 0;
  grid-column: auto / span 3;
}

.filters-primary > :deep(.compact) {
  grid-column: auto / span 2;
}
.filters-primary > :deep(.medium) {
  grid-column: auto / span 4;
}
.filters-primary > :deep(.wide) {
  grid-column: auto / span 6;
}
.filters-primary > :deep(.large) {
  grid-column: auto / span 8;
}
.filters-primary > :deep(.xlarge) {
  grid-column: auto / span 9;
}
.filters-primary > :deep(.full) {
  grid-column: 1 / -1;
}

.filters-primary :deep(.input-group),
.filters-primary :deep(.select),
.filters-primary :deep(.multi-select),
.filters-primary :deep(.date-picker),
.filters-primary :deep(.textarea-group),
.filters-primary :deep(.pill-selector) {
  width: 100%;
  min-width: 0;
}

.filters-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  align-self: end;
  min-width: 0;
}

.filters-actions :deep(.base-button) {
  min-width: 96px;
}

.filters-actions--stacked {
  padding: 0 16px 16px;
  justify-content: flex-end;
}

.filters-toggle-icon {
  width: 14px;
  height: 14px;
  transition: transform 0.2s ease;
}

.filters-toggle-icon--open {
  transform: rotate(180deg);
}

.filters-extended {
  display: grid;
  gap: 12px 14px;
  padding: 14px 16px 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-background-soft);
  border-radius: 0 0 12px 12px;
}

.filters-extended--stacked {
  padding: 0 0 0;
  border-top: none;
  background: transparent;
  border-radius: 0;
}

.filters-extended > * {
  min-width: 0;
  grid-column: auto / span 3;
}

.filters-extended > :deep(.compact) {
  grid-column: auto / span 2;
}
.filters-extended > :deep(.medium) {
  grid-column: auto / span 4;
}
.filters-extended > :deep(.wide) {
  grid-column: auto / span 6;
}
.filters-extended > :deep(.large) {
  grid-column: auto / span 8;
}
.filters-extended > :deep(.xlarge) {
  grid-column: auto / span 9;
}
.filters-extended > :deep(.full) {
  grid-column: 1 / -1;
}

.filters-extended :deep(.input-group),
.filters-extended :deep(.select),
.filters-extended :deep(.multi-select),
.filters-extended :deep(.date-picker),
.filters-extended :deep(.textarea-group),
.filters-extended :deep(.pill-selector) {
  width: 100%;
  min-width: 0;
}

@media (max-width: 1440px) {
  .filters-row {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .filters-actions {
    justify-content: flex-start;
  }

  .filters-actions--stacked {
    justify-content: flex-start;
  }
}

@media (max-width: 960px) {
  .filters-primary > *,
  .filters-extended > * {
    grid-column: auto / span 6;
  }

  .filters-primary > :deep(.compact),
  .filters-extended > :deep(.compact),
  .filters-primary > :deep(.medium),
  .filters-extended > :deep(.medium) {
    grid-column: auto / span 6;
  }

  .filters-primary > :deep(.wide),
  .filters-primary > :deep(.large),
  .filters-primary > :deep(.xlarge),
  .filters-primary > :deep(.full),
  .filters-extended > :deep(.wide),
  .filters-extended > :deep(.large),
  .filters-extended > :deep(.xlarge),
  .filters-extended > :deep(.full) {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .filters-row {
    padding: 12px;
    gap: 12px;
  }
  .filters-body {
    padding: 12px;
  }
  .filters-primary--with-extended {
    padding-bottom: 12px;
  }
  .filters-extended {
    padding: 12px;
  }
  .filters-extended--stacked {
    padding: 12px 0 0;
  }
  .filters-actions--stacked {
    padding: 12px;
  }

  .filters-primary > *,
  .filters-primary > :deep(.compact),
  .filters-primary > :deep(.medium),
  .filters-primary > :deep(.wide),
  .filters-primary > :deep(.large),
  .filters-primary > :deep(.xlarge),
  .filters-primary > :deep(.full),
  .filters-extended > *,
  .filters-extended > :deep(.compact),
  .filters-extended > :deep(.medium),
  .filters-extended > :deep(.wide),
  .filters-extended > :deep(.large),
  .filters-extended > :deep(.xlarge),
  .filters-extended > :deep(.full) {
    grid-column: 1 / -1;
  }

  .filters-actions,
  .filters-actions--stacked {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .filters-actions :deep(.base-button),
  .filters-actions--stacked :deep(.base-button) {
    width: 100%;
    min-width: 0;
  }
}
</style>
