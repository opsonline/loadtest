import { useUserStore } from '@/store/user'

/**
 * 检查用户是否有指定权限
 */
export function hasPermission(permission) {
  const userStore = useUserStore()
  
  switch (permission) {
    case 'manage-users':
      return userStore.canManageUsers
    case 'create-scenarios':
      return userStore.canCreateScenarios
    case 'run-tests':
      return userStore.canRunTests
    case 'delete-reports':
      return userStore.canDeleteReports
    case 'admin':
      return userStore.isAdmin
    case 'viewer':
      return userStore.isViewer
    default:
      return true
  }
}

/**
 * 注册权限指令
 */
export default {
  install(app) {
    app.directive('permission', {
      mounted(el, binding) {
        const { value } = binding
        const hasPerm = hasPermission(value)
        
        if (!hasPerm) {
          el.style.display = 'none'
          // 或者可以添加注释说明权限不足
          console.warn(`Permission denied for directive: ${value}`)
        }
      },
      updated(el, binding) {
        const { value } = binding
        const hasPerm = hasPermission(value)
        
        if (!hasPerm) {
          el.style.display = 'none'
        } else {
          el.style.display = ''
        }
      }
    })
  }
}