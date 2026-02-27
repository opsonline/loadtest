<template>
  <div class="variables-page">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.back()">
          <el-icon><Back /></el-icon>返回
        </el-button>
        <h2>环境变量管理 - {{ environment?.name }}</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="addVariable">
          <el-icon><Plus /></el-icon>添加变量
        </el-button>
        <el-button @click="saveVariables" :loading="saving">
          <el-icon><Check /></el-icon>保存
        </el-button>
      </div>
    </div>

    <el-card class="env-info-card" v-if="environment">
      <template #header>
        <div class="card-header">
          <span>环境信息</span>
          <el-tag v-if="environment.is_default" type="success">默认环境</el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="环境名称">{{ environment.name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(environment.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="环境描述" :span="2">
          {{ environment.description || '暂无描述' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="variables-card">
      <template #header>
        <div class="card-header">
          <span>变量列表 ({{ variables.length }})</span>
        </div>
      </template>
      
      <el-table :data="variables" style="width: 100%">
        <el-table-column prop="name" label="变量名" width="180" />
        <el-table-column prop="value" label="变量值">
          <template #default="{ row }">
            <div v-if="editingIndex === $index">
              <el-input 
                v-model="editingRow.value" 
                :type="row.var_type === 'secret' ? 'password' : 'text'"
                :show-password="row.var_type === 'secret'"
                placeholder="输入变量值"
              />
            </div>
            <div v-else>
              <span v-if="row.var_type === 'secret'" class="secret-value">******</span>
              <span v-else>{{ row.value }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="var_type" label="类型" width="100">
          <template #default="{ row }">
            <el-select v-if="editingIndex === $index" v-model="editingRow.var_type" size="small">
              <el-option label="文本" value="text" />
              <el-option label="敏感" value="secret" />
              <el-option label="引用" value="reference" />
            </el-select>
            <el-tag v-else size="small">{{ getVarTypeText(row.var_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scope" label="作用域" width="100">
          <template #default="{ row }">
            <el-select v-if="editingIndex === $index" v-model="editingRow.scope" size="small">
              <el-option label="全局" value="global" />
              <el-option label="项目" value="project" />
              <el-option label="场景" value="scenario" />
            </el-select>
            <el-tag v-else size="small">{{ getScopeText(row.scope) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述">
          <template #default="{ row }">
            <el-input 
              v-if="editingIndex === $index" 
              v-model="editingRow.description" 
              size="small"
              placeholder="描述"
            />
            <span v-else class="text-muted">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }">
            <template v-if="editingIndex === $index">
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button size="small" type="primary" @click="confirmEdit($index)">确定</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="startEdit(row, $index)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteVariable($index)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="variables.length === 0" description="暂无变量，点击上方按钮添加" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Back, Check } from '@element-plus/icons-vue'
import { environmentApi } from '@/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const environment = ref(null)
const variables = ref([])
const editingIndex = ref(-1)
const editingRow = ref({})

onMounted(() => {
  fetchEnvironment()
})

const fetchEnvironment = async () => {
  try {
    loading.value = true
    const envId = route.params.id
    const data = await environmentApi.get(envId)
    environment.value = data
    variables.value = data.variables || []
  } catch (error) {
    console.error('Failed to fetch environment:', error)
    ElMessage.error('获取环境信息失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const getVarTypeText = (type) => {
  const map = { 'text': '文本', 'secret': '敏感', 'reference': '引用' }
  return map[type] || type
}

const getScopeText = (scope) => {
  const map = { 'global': '全局', 'project': '项目', 'scenario': '场景' }
  return map[scope] || scope
}

const formatDate = (dateStr) => {
  return dateStr ? dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const addVariable = () => {
  variables.value.push({
    name: '',
    value: '',
    var_type: 'text',
    scope: 'global',
    description: ''
  })
}

const startEdit = (row, index) => {
  editingIndex.value = index
  editingRow.value = { ...row }
}

const cancelEdit = () => {
  editingIndex.value = -1
  editingRow.value = {}
}

const confirmEdit = (index) => {
  if (!editingRow.value.name) {
    ElMessage.warning('变量名不能为空')
    return
  }
  variables.value[index] = { ...editingRow.value }
  cancelEdit()
}

const deleteVariable = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除该变量吗？', '提示', { type: 'warning' })
    variables.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete variable error:', error)
    }
  }
}

const saveVariables = async () => {
  try {
    saving.value = true
    
    // 验证
    const names = variables.value.map(v => v.name)
    const duplicates = names.filter((name, index) => names.indexOf(name) !== index)
    if (duplicates.length > 0) {
      ElMessage.error('变量名不能重复')
      return
    }
    
    await environmentApi.update(environment.value.id, {
      ...environment.value,
      variables: variables.value
    })
    
    ElMessage.success('保存成功')
    await fetchEnvironment()
  } catch (error) {
    console.error('Save variables error:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.variables-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
}

.header-right {
  display: flex;
  gap: 10px;
}

.env-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.variables-card {
  margin-bottom: 20px;
}

.secret-value {
  color: #999;
  font-style: italic;
}

.text-muted {
  color: #999;
}
</style>