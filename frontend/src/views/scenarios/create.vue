<template>
  <div class="scenario-form">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑场景' : '创建场景' }}</h2>
      <div>
        <el-button @click="$router.back()">取消</el-button>
        <el-button type="primary" @click="saveScenario" :loading="saving">保存</el-button>
      </div>
    </div>

    <el-card class="mb-20">
      <el-form :model="form" label-width="100px">
        <el-form-item label="场景名称">
          <el-input v-model="form.name" placeholder="输入场景名称" />
        </el-form-item>
        <el-form-item label="场景描述">
          <el-input v-model="form.description" type="textarea" placeholder="输入场景描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="默认用户数">
              <el-input-number v-model="form.default_users" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="每秒生成">
              <el-input-number v-model="form.default_spawn_rate" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="压测时长">
              <el-input-number v-model="form.default_duration" :min="1" :max="3600" style="width: 100%">
                <template #append>秒</template>
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>请求列表</span>
          <el-button type="primary" @click="addRequest">
            <el-icon><Plus /></el-icon>添加请求
          </el-button>
        </div>
      </template>

      <el-collapse v-model="activeRequests">
        <el-collapse-item v-for="(req, index) in form.requests" :key="index" :name="index">
          <template #title>
            <div class="request-title">
              <el-tag :type="getMethodType(req.method)">{{ req.method }}</el-tag>
              <span class="ml-2">{{ req.name || `请求 ${index + 1}` }}</span>
              <el-icon class="delete-icon" @click.stop="removeRequest(index)"><Delete /></el-icon>
            </div>
          </template>

          <el-form :model="req" label-width="100px">
            <el-form-item label="请求名称">
              <el-input v-model="req.name" placeholder="输入请求名称" />
            </el-form-item>
            <el-form-item label="请求方法">
              <el-radio-group v-model="req.method">
                <el-radio-button label="GET" />
                <el-radio-button label="POST" />
                <el-radio-button label="PUT" />
                <el-radio-button label="DELETE" />
                <el-radio-button label="PATCH" />
              </el-radio-group>
            </el-form-item>
            <el-form-item label="请求URL">
              <el-input v-model="req.url" placeholder="https://api.example.com/users" />
            </el-form-item>
            <el-form-item label="请求头">
              <el-input v-model="req.headersText" type="textarea" :rows="3" 
                placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}' />
            </el-form-item>
            <el-form-item label="请求体类型">
              <el-radio-group v-model="req.body_type">
                <el-radio label="none">无</el-radio>
                <el-radio label="json">JSON</el-radio>
                <el-radio label="form">表单</el-radio>
                <el-radio label="file">文件</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="请求体" v-if="req.body_type !== 'none'">
              <el-input v-model="req.body" type="textarea" :rows="5" placeholder="请求体内容" />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="权重">
                  <el-input-number v-model="req.weight" :min="1" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="思考时间">
                  <el-input-number v-model="req.think_time" :min="0" :step="0.1" style="width: 100%">
                    <template #append>秒</template>
                  </el-input-number>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间">
                  <el-input-number v-model="req.timeout" :min="1" :max="300" style="width: 100%">
                    <template #append>秒</template>
                  </el-input-number>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { scenarioApi } from '@/api'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)
const activeRequests = ref([0])

const form = ref({
  name: '',
  description: '',
  default_users: 10,
  default_spawn_rate: 1,
  default_duration: 60,
  requests: []
})

onMounted(() => {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    fetchScenario(id)
  } else {
    // 新建场景，添加一个默认请求
    addRequest()
  }
})

const fetchScenario = async (id) => {
  try {
    const data = await scenarioApi.detail(id)
    // 转换 headers 为文本
    const requests = (data.requests || []).map(req => ({
      ...req,
      headersText: req.headers ? JSON.stringify(req.headers, null, 2) : ''
    }))
    form.value = {
      name: data.name,
      description: data.description || '',
      default_users: data.default_users || 10,
      default_spawn_rate: data.default_spawn_rate || 1,
      default_duration: data.default_duration || 60,
      requests
    }
    if (form.value.requests.length > 0) {
      activeRequests.value = [0]
    }
  } catch (error) {
    console.error('Failed to fetch scenario:', error)
    ElMessage.error('获取场景详情失败')
  }
}

const getMethodType = (method) => {
  const map = { 'GET': 'success', 'POST': 'primary', 'PUT': 'warning', 'DELETE': 'danger', 'PATCH': 'info' }
  return map[method] || ''
}

const addRequest = () => {
  form.value.requests.push({
    name: '',
    method: 'GET',
    url: '',
    headersText: '',
    body_type: 'none',
    body: '',
    weight: 1,
    think_time: 1,
    timeout: 30
  })
  activeRequests.value = [form.value.requests.length - 1]
}

const removeRequest = (index) => {
  form.value.requests.splice(index, 1)
}

const saveScenario = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入场景名称')
    return
  }
  
  saving.value = true
  
  // 转换 headers
  const requests = form.value.requests.map((req, index) => {
    let headers = {}
    try {
      if (req.headersText) {
        headers = JSON.parse(req.headersText)
      }
    } catch (e) {
      console.error('Invalid headers JSON:', e)
    }
    
    return {
      name: req.name || `请求 ${index + 1}`,
      method: req.method,
      url: req.url,
      headers,
      body_type: req.body_type || 'none',
      body: req.body || null,
      weight: req.weight || 1,
      think_time: req.think_time || 0,
      timeout: req.timeout || 30,
      order: index
    }
  })
  
  const data = {
    name: form.value.name,
    description: form.value.description,
    default_users: form.value.default_users,
    default_spawn_rate: form.value.default_spawn_rate,
    default_duration: form.value.default_duration,
    requests
  }
  
  try {
    if (isEdit.value) {
      await scenarioApi.update(route.params.id, data)
      ElMessage.success('更新成功')
    } else {
      await scenarioApi.create(data)
      ElMessage.success('创建成功')
    }
    router.push('/scenarios')
  } catch (error) {
    console.error('Save scenario error:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.scenario-form {
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

.mb-20 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.request-title {
  display: flex;
  align-items: center;
  flex: 1;
  padding-right: 20px;
}

.ml-2 {
  margin-left: 8px;
}

.delete-icon {
  margin-left: auto;
  cursor: pointer;
  color: #f56c6c;
}

.delete-icon:hover {
  color: #f89898;
}
</style>
