import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Dashboard' }
      },
      {
        path: '/scenarios',
        name: 'Scenarios',
        component: () => import('@/views/scenarios/index.vue'),
        meta: { title: '场景管理', icon: 'List' }
      },
      {
        path: '/scenarios/create',
        name: 'ScenarioCreate',
        component: () => import('@/views/scenarios/create.vue'),
        meta: { title: '创建场景', hidden: true }
      },
      {
        path: '/scenarios/:id/edit',
        name: 'ScenarioEdit',
        component: () => import('@/views/scenarios/edit.vue'),
        meta: { title: '编辑场景', hidden: true }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/reports/index.vue'),
        meta: { title: '报告管理', icon: 'Document' }
      },
      {
        path: '/reports/:id',
        name: 'ReportDetail',
        component: () => import('@/views/reports/detail.vue'),
        meta: { title: '报告详情', hidden: true }
      },
      {
        path: '/environments',
        name: 'Environments',
        component: () => import('@/views/environments/index.vue'),
        meta: { title: '环境变量', icon: 'Setting' }
      },
      {
        path: '/environments/:id/variables',
        name: 'EnvironmentVariables',
        component: () => import('@/views/environments/variables.vue'),
        meta: { title: '变量管理', hidden: true }
      },
      {
        path: '/datasources',
        name: 'Datasources',
        component: () => import('@/views/datasources/index.vue'),
        meta: { title: '数据源', icon: 'DataLine' }
      },
      {
        path: '/api-tests',
        name: 'ApiTests',
        component: () => import('@/views/api-tests/index.vue'),
        meta: { title: '接口测试', icon: 'Connection' }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/users/list.vue'),
        meta: { title: '用户管理', icon: 'User', permission: 'manage-users' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  console.log('Route guard - to:', to.path, 'from:', from.path)
  console.log('Route guard - userStore.token:', userStore.token)
  console.log('Route guard - localStorage token:', localStorage.getItem('token'))
  
  if (to.meta.public) {
    console.log('Route is public, allowing access')
    next()
  } else if (!userStore.token) {
    console.log('No token found, redirecting to login')
    next('/login')
  } else {
    console.log('Token found, proceeding with permission check')
    
    // 如果还没有加载权限信息，则加载它
    if (!userStore.permissions || Object.keys(userStore.permissions).length === 0) {
      console.log('Loading permissions...')
      await userStore.loadPermissions()
      console.log('Permissions loaded:', userStore.permissions)
    }
    
    // 检查路由权限
    const requiredPermission = to.meta.permission
    if (requiredPermission) {
      const hasPerm = (() => {
        switch (requiredPermission) {
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
          default:
            return true
        }
      })()
      
      if (!hasPerm) {
        // 如果没有权限，跳转到首页或其他适当的页面
        console.warn(`Access denied to route: ${to.path}`)
        next('/dashboard') // 或者可以跳转到一个无权限提示页面
        return
      }
    }
    
    console.log('Route access granted')
    next()
  }
})

export default router
