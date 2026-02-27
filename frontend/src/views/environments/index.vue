<template>
  <div class="environments-page">
    <div class="page-header">
      <h2>环境变量管理</h2>
      <div class="header-actions">
        <el-button @click="importEnvironments">
          <el-icon><Upload /></el-icon>导入
        </el-button>
        <el-button @click="exportEnvironments" :disabled="environments.length === 0">
          <el-icon><Download /></el-icon>导出
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建环境
        </el-button>
      </div>
    </div>

    <input
      ref="importInput"
      type="file"
      accept=".json"
      style="display: none"
      @change="handleImportFile"
    />

    <el-row :gutter="20">
      <el-col :span="8" v-for="env in environments" :key="env.id">
        <el-card class="environment-card" :class="{ 'is-default': env.is_default }">
          <template #header>
            <div class="card-header">
              <span class="env-name">
                {{ env.name }}
                <el-tag v-if="env.is_default" type="success" size="small">默认</el-tag>
              </span>
              <el-dropdown>
                <el-icon class="more-icon"><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="setDefault(env)">设为默认</el-dropdown-item>
                    <el-dropdown-item @click="editEnvironment(env)">编辑</el-dropdown-item>
                    <el-dropdown-item @click="deleteEnvironment(env)">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <div class="env-description">{{ env.description || '暂无描述' }}</div>
<div class="env-stats">
            <el-tag type="info">{{ env.variable_count }} 个变量</el-tag>
          </div>
          <div class="env-actions">
            <el-button type="primary" link @click="goToVariablesPage(env)">管理变量</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

<!-- 创建/编辑环境对话框 -->
    <el-dialog v-model="showCreateDialog" :title="isEdit ? '编辑环境' : '创建环境'" width="500px">
      <el-form :model="envForm" label-width="100px">
        <el-form-item label="环境名称">
          <el-input v-model="envForm.name" placeholder="输入环境名称" />
        </el-form-item>
        <el-form-item label="环境描述">
          <el-input v-model="envForm.description" type="textarea" placeholder="输入环境描述" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="envForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEnvironment" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, More, Upload, Download } from '@element-plus/icons-vue'
import { environmentApi } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const environments = ref([])
const showCreateDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentEnv = ref(null)
const importInput = ref(null)

const envForm = ref({
  name: '',
  description: '',
  is_default: false
})

// 调用 API 获取环境列表
onMounted(() => {
  fetchEnvironments()
})

const fetchEnvironments = async () => {
  try {
    loading.value = true
    const data = await environmentApi.list()
    environments.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch environments:', error)
    ElMessage.error('获取环境列表失败')
  } finally {
    loading.value = false
  }
}

const getVarTypeText = (type) => {
  const map = { 'text': '文本', 'secret': '敏感', 'reference': '引用' }
  return map[type] || type
}

const saveEnvironment = async () => {
  try {
    saving.value = true
    if (isEdit.value) {
      await environmentApi.update(currentEnv.value.id, envForm.value)
      ElMessage.success('更新成功')
    } else {
      await environmentApi.create(envForm.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    fetchEnvironments()
  } catch (error) {
    console.error('Save environment error:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const editEnvironment = (env) => {
  isEdit.value = true
  envForm.value = { ...env }
  showCreateDialog.value = true
}

const deleteEnvironment = async (env) => {
  try {
    await ElMessageBox.confirm('确定要删除该环境吗？', '提示', { type: 'warning' })
    await environmentApi.delete(env.id)
    ElMessage.success('删除成功')
    fetchEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete environment error:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const setDefault = async (env) => {
  try {
    await environmentApi.setDefault(env.id)
    ElMessage.success('设置成功')
    fetchEnvironments()
  } catch (error) {
    console.error('Set default environment error:', error)
    ElMessage.error(error.message || '设置失败')
  }
}

const goToVariablesPage = (env) => {
  router.push(`/environments/${env.id}/variables`)
}

const importEnvironments = () => {
  importInput.value?.click()
}

const handleImportFile = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  try {
    const text = await file.text()
    const importData = JSON.parse(text)
    
    if (!Array.isArray(importData)) {
      ElMessage.error('导入文件格式不正确')
      return
    }
    
    let importCount = 0
    for (const envData of importData) {
      if (envData.name) {
        try {
          await environmentApi.create({
            name: envData.name,
            description: envData.description || '',
            is_default: false,
            variables: envData.variables || []
          })
          importCount++
        } catch (e) {
          console.error('Failed to import environment:', envData.name, e)
        }
      }
    }
    
    ElMessage.success(`成功导入 ${importCount} 个环境`)
    fetchEnvironments()
  } catch (error) {
    console.error('Import error:', error)
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    event.target.value = ''
  }
}

const exportEnvironments = async () => {
  if (environments.value.length === 0) {
    ElMessage.warning('没有可导出的环境')
    return
  }
  
  try {
    const exportData = await Promise.all(
      environments.value.map(async (env) => {
        try {
          const detail = await environmentApi.get(env.id)
          return {
            name: env.name,
            description: env.description,
            is_default: env.is_default,
            variables: detail.variables || []
          }
        } catch (e) {
          return {
            name: env.name,
            description: env.description,
            is_default: env.is_default,
            variables: []
          }
        }
      })
    )
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `environments_export_${dayjs().format('YYYYMMDD_HHmmss')}.json`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败')
  }
}
</script>

<style scoped>
.environments-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.environment-card {
  margin-bottom: 20px;
}

.environment-card.is-default {
  border: 2px solid #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.env-name {
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.more-icon {
  cursor: pointer;
  padding: 4px;
}

.env-description {
  color: #666;
  margin-bottom: 15px;
  min-height: 40px;
}

.env-stats {
  margin-bottom: 15px;
}
</style>
