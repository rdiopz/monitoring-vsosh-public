import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@services/api'

export const useRolesStore = defineStore('roles', () => {
  // Состояния
  const roles = ref([])
  const loading = ref(false)

  // Загрузить список ролей
  const fetchRoles = async () => {
    loading.value = true
    try {
      const response = await authAPI.getRoles()
      roles.value = response.data.results || response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  // Получить роль по ID
  const getRoleById = (roleId) => {
    return roles.value.find((r) => r.role_id === roleId)
  }

  // Получить название роли по ID
  const getRoleNameById = (roleId) => {
    const role = getRoleById(roleId)
    return role ? role.name : null
  }

  // Сбросить состояние
  const resetState = () => {
    roles.value = []
  }

  return {
    roles,
    loading,

    fetchRoles,
    getRoleById,
    getRoleNameById,
    resetState,
  }
})
