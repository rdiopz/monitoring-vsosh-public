import { ref } from 'vue'
import { useToast } from 'vue-toastification'

export function useImport(importFunction, onSuccess) {
  const toast = useToast()
  const importResponse = ref(null)
  const isDragOver = ref(false)
  const isImporting = ref(false)
  const fileInputRef = ref(null)

  const validateFile = (file) => {
    const validExtentsions = ['.xlsx', '.csv']
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()

    if (!validExtentsions.includes(fileExtension)) {
      toast.error('Поддерживаются только файлы XLSX и CSV')
      return false
    }
    return true
  }

  // Обработка при нажатии кнопки для передачи файла через проводник
  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0]
    if (file) {
      await handleImport(file)
    }
    event.target.value = ''
  }

  const triggerFileInput = () => {
    fileInputRef.value?.click()
  }

  // Для UI дизайна при перетаскивании
  const handleDragOver = (event) => {
    event.preventDefault()
    isDragOver.value = true
  }

  const handleDragLeave = () => {
    isDragOver.value = false
  }

  // Обработка передачи файла через перетаскивание
  const handleDrop = async (event) => {
    event.preventDefault()
    isDragOver.value = false

    const file = event.dataTransfer.files[0]
    if (file) {
      await handleImport(file)
    }
  }

  const handleImport = async (file) => {
    if (!validateFile(file)) return

    importResponse.value = null
    isImporting.value = true
    try {
      importResponse.value = await importFunction(file)
      if (onSuccess) onSuccess()
    } catch (error) {
      importResponse.value = error.response?.data?.errors ? error.response.data : null
    } finally {
      isImporting.value = false
    }
  }

  const cleanErrorMessage = (error) => {
    if (!error) return ''
    return error.replace(/^Строка\s*\d+\s*:\s*/i, '').trim()
  }

  const clearImportResponse = () => {
    importResponse.value = null
  }

  return {
    importResponse,
    isDragOver,
    isImporting,
    fileInputRef,

    handleFileSelect,
    triggerFileInput,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    cleanErrorMessage,
    clearImportResponse,
  }
}
