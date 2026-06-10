import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'

export function useExport(store, exportFunction) {
  const toast = useToast()
  const exportError = ref('')

  let columnsOrder = []
  const defaultColumns = [...store.ui.exportColumns]

  const exportWithFilters = computed({
    get: () => store.ui.exportWithFilters,
    set: (val) => {
      store.ui.exportWithFilters = val
    },
  })

  const setColumnsOrder = (keys) => {
    columnsOrder = keys
  }

  const selectedExportColumns = computed(() => store.ui.exportColumns)

  const toggleColumn = (key) => {
    if (store.ui.exportColumns.includes(key)) {
      store.ui.exportColumns = store.ui.exportColumns.filter((k) => k !== key)
    } else {
      store.ui.exportColumns = columnsOrder.filter(
        (k) => store.ui.exportColumns.includes(k) || k === key,
      )
    }
  }

  const toggleAll = (allKeys) => {
    if (store.ui.exportColumns.length === allKeys.length) {
      store.ui.exportColumns = []
    } else {
      store.ui.exportColumns = [...allKeys]
    }
  }

  const resetToDefault = () => {
    store.ui.exportColumns = [...defaultColumns]
  }

  const handleExport = async () => {
    exportError.value = ''

    if (selectedExportColumns.value.length === 0) {
      exportError.value = 'Выберите хотя бы одну колонку для экспорта'
      toast.error(exportError.value)
      return
    }

    await exportFunction(selectedExportColumns.value, exportWithFilters.value)
  }

  return {
    exportWithFilters,
    exportError,
    selectedExportColumns,
    setColumnsOrder,
    toggleColumn,
    toggleAll,
    resetToDefault,
    handleExport,
  }
}
