import api from '@/utils/request'

export const userApi = {
  // 用户注册
  register: (data) => api.post('/users/register/', data),
  
  // 用户登录
  login: (data) => api.post('/users/login/', data),
  
  // 获取用户信息
  profile: () => api.get('/users/profile/'),
  
  // 获取用户列表
  list: (params) => api.get('/users/', { params }),
  
  // 获取用户详情
  detail: (id) => api.get(`/users/${id}/`),
  
  // 删除用户
  delete: (id) => api.delete(`/users/${id}/`),
  
  // 更新用户角色
  updateUserRole: (id, data) => api.patch(`/users/${id}/role/`, data),
  
  // 获取当前用户权限
  getPermissions: () => api.get('/users/my-permissions/')
}

export const scenarioApi = {
  // 获取场景列表
  list: (params) => api.get('/scenarios/', { params }),
  
  // 创建场景
  create: (data) => api.post('/scenarios/', data),
  
  // 获取场景详情
  detail: (id) => api.get(`/scenarios/${id}/`),
  
  // 更新场景
  update: (id, data) => api.put(`/scenarios/${id}/`, data),
  
  // 删除场景
  delete: (id) => api.delete(`/scenarios/${id}/`),
  
  // 复制场景
  copy: (id) => api.post(`/scenarios/${id}/copy/`),
  
  // 导入 HAR
  importHar: (data) => {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (key === 'resource_types') {
        formData.append(key, data[key].join(','))
      } else {
        formData.append(key, data[key])
      }
    })
    return api.post('/scenarios/import-har/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const reportApi = {
  // 获取报告列表
  list: (params) => api.get('/reports/', { params }),
  
  // 创建报告
  create: (data) => api.post('/reports/', data),
  
  // 获取报告详情
  detail: (id) => api.get(`/reports/${id}/`),
  
  // 删除报告
  delete: (id) => api.delete(`/reports/${id}/`),
  
  // 运行压测
  run: (id) => api.post(`/reports/${id}/run/`),
  
  // 停止压测
  stop: (id) => api.post(`/reports/${id}/stop/`),
  
  // 获取压测统计
  stats: (id) => api.get(`/reports/${id}/stats/`),
  
  // 对比报告
  compare: (data) => api.post('/reports/compare/', data)
}

// WebSocket 连接工具
export const websocketUtils = {
  connect: (reportId) => {
    // 获取当前协议并替换为ws/wss协议
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const token = localStorage.getItem('token')
    return new WebSocket(`${protocol}//${host}/ws/load-test/${reportId}/?token=${token}`)
  },
  
  send: (ws, data) => {
    ws.send(JSON.stringify(data))
  }
}

// 辅助函数：下载文件
function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// 报告导出功能
export const reportExportApi = {
  // 导出报告为PDF
  exportPdf: async (reportId) => {
    try {
      const response = await fetch(`${api.defaults.baseURL}/reports/${reportId}/export/pdf/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const blob = await response.blob();
      const filename = `report_${reportId}.pdf`;
      downloadBlob(blob, filename);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  },
  
  // 导出报告为Excel
  exportExcel: async (reportId) => {
    try {
      const response = await fetch(`${api.defaults.baseURL}/reports/${reportId}/export/excel/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const blob = await response.blob();
      const filename = `report_${reportId}.xlsx`;
      downloadBlob(blob, filename);
    } catch (error) {
      console.error('Error downloading Excel:', error);
      throw error;
    }
  }
}

export const environmentApi = {
  // 获取环境列表
  list: (params) => api.get('/environments/', { params }),
  
  // 获取环境详情
  get: (id) => api.get(`/environments/${id}/`),
  
  // 创建环境
  create: (data) => api.post('/environments/', data),
  
  // 更新环境
  update: (id, data) => api.put(`/environments/${id}/`, data),
  
  // 删除环境
  delete: (id) => api.delete(`/environments/${id}/`),
  
  // 设置默认环境
  setDefault: (id) => api.post(`/environments/${id}/set-default/`),
  
  // 获取默认环境
  getDefault: () => api.get('/environments/default/'),
  
  // 预览变量替换
  preview: (id, data) => api.post(`/environments/${id}/preview/`, data)
}

export const datasourceApi = {
  // 获取数据源列表
  list: (params) => api.get('/datasources/', { params }),
  
  // 获取数据源详情
  get: (id) => api.get(`/datasources/${id}/`),
  
  // 创建数据源
  create: (data) => api.post('/datasources/', data),
  
  // 更新数据源
  update: (id, data) => api.put(`/datasources/${id}/`, data),
  
  // 删除数据源
  delete: (id) => api.delete(`/datasources/${id}/`),
  
  // 测试连接
  test: (id) => api.post(`/datasources/${id}/test/`),
  
  // 预览数据
  preview: (id, params) => api.get(`/datasources/${id}/preview/`, { params }),
  
  // 上传文件
  upload: (data) => {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      formData.append(key, data[key])
    })
    return api.post('/datasources/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const apiTestApi = {
  // 获取测试套件列表
  listSuites: (params) => api.get('/api-tests/suites/', { params }),
  
  // 创建测试套件
  createSuite: (data) => api.post('/api-tests/suites/', data),
  
  // 更新测试套件
  updateSuite: (id, data) => api.put(`/api-tests/suites/${id}/`, data),
  
  // 删除测试套件
  deleteSuite: (id) => api.delete(`/api-tests/suites/${id}/`),
  
  // 获取测试用例列表
  listCases: (suiteId, params) => api.get(`/api-tests/suites/${suiteId}/cases/`, { params }),
  
  // 创建测试用例
  createCase: (suiteId, data) => api.post(`/api-tests/suites/${suiteId}/cases/`, data),
  
  // 更新测试用例
  updateCase: (id, data) => api.put(`/api-tests/cases/${id}/`, data),
  
  // 删除测试用例
  deleteCase: (id) => api.delete(`/api-tests/cases/${id}/`),
  
  // 执行测试
  execute: (data) => api.post('/api-tests/execute/', data),
  
  // 执行单个请求
  executeRequest: (data) => api.post('/api-tests/execute-request/', data),
  
  // 获取测试结果列表
  listResults: (params) => api.get('/api-tests/results/', { params })
}
