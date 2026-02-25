import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  // State - 从localStorage读取
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const permissions = ref({})
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => permissions.value.is_admin)
  const isViewer = computed(() => permissions.value.is_viewer)
  const canManageUsers = computed(() => permissions.value.can_manage_users)
  const canCreateScenarios = computed(() => permissions.value.can_create_scenarios)
  const canRunTests = computed(() => permissions.value.can_run_tests)
  const canDeleteReports = computed(() => permissions.value.can_delete_reports)
  
  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  const setUserInfo = (info) => {
    userInfo.value = info
    if (info) {
      localStorage.setItem('userInfo', JSON.stringify(info))
    }
  }
  
  const setPermissions = (perms) => {
    permissions.value = perms || {}
  }
  
  const loadPermissions = async () => {
    try {
      const response = await userApi.getPermissions()
      setPermissions(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to load permissions:', error)
      return {}
    }
  }
  
  const logout = () => {
    token.value = ''
    userInfo.value = null
    permissions.value = {}
    localStorage.removeItem('token')
  }
  
  return {
    token,
    userInfo,
    permissions,
    isLoggedIn,
    isAdmin,
    isViewer,
    canManageUsers,
    canCreateScenarios,
    canRunTests,
    canDeleteReports,
    setToken,
    setUserInfo,
    setPermissions,
    loadPermissions,
    logout
  }
})
