<template>
  <div class="scenarios-page">
    <div class="page-header">
      <h2>场景管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>导入 HAR
        </el-button>
        <el-button type="success" @click="$router.push('/scenarios/create')">
          <el-icon><Plus /></el-icon>创建场景
        </el-button>
      </div>
    </div>

    <el-card>
      <el-table :data="scenarios" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="场景名称" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" @click="editScenario(row)">{{ row.name }}</el-link>
            <el-tag v-if="row.is_imported_from_har" size="small" type="info" class="ml-2">HAR</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="request_count" label="请求数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="runTest(row)">运行</el-button>
            <el-button link type="primary" @click="editScenario(row)">编辑</el-button>
            <el-button link type="primary" @click="copyScenario(row)">复制</el-button>
            <el-button link type="danger" @click="deleteScenario(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- HAR 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入 HAR 文件" width="600px">
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="HAR 文件">
          <el-upload
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".har"
            limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="场景名称">
          <el-input v-model="importForm.name" placeholder="输入场景名称" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-checkbox-group v-model="importForm.resource_types">
            <el-checkbox label="xhr">XHR</el-checkbox>
            <el-checkbox label="document">Document</el-checkbox>
            <el-checkbox label="other">Other</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Host 替换">
          <el-input v-model="importForm.host_replacement" placeholder="例如: api.example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importHar" :loading="importing">导入</el-button>
      </template>
    </el-dialog>

    <!-- 运行压测对话框 -->
    <el-dialog v-model="showRunDialog" title="运行压测" width="500px">
      <el-form :model="runForm" label-width="120px">
        <el-form-item label="并发用户数">
          <el-slider v-model="runForm.users" :max="1000" show-input />
        </el-form-item>
        <el-form-item label="每秒生成数">
          <el-slider v-model="runForm.spawn_rate" :max="100" show-input />
        </el-form-item>
        <el-form-item label="压测时长(秒)">
          <el-slider v-model="runForm.duration" :max="3600" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRunDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRun" :loading="running">开始压测</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, UploadFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { scenarioApi, reportApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const scenarios = ref([])
const showImportDialog = ref(false)
const showRunDialog = ref(false)
const importing = ref(false)
const running = ref(false)
const currentScenario = ref(null)

const importForm = ref({
  name: '',
  resource_types: ['xhr', 'document'],
  host_replacement: '',
  file: null
})

const runForm = ref({
  users: 10,
  spawn_rate: 1,
  duration: 60
})

// 调用 API 获取场景列表
onMounted(() => {
  fetchScenarios()
})

const fetchScenarios = async () => {
  try {
    loading.value = true
    const data = await scenarioApi.list()
    scenarios.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch scenarios:', error)
    ElMessage.error('获取场景列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const handleFileChange = (file) => {
  if (!importForm.value.name) {
    importForm.value.name = file.name.replace('.har', '')
  }
  importForm.value.file = file.raw
}

const importHar = async () => {
  if (!importForm.value.file) {
    ElMessage.warning('请选择HAR文件')
    return
  }
  if (!importForm.value.name) {
    ElMessage.warning('请输入场景名称')
    return
  }
  
  try {
    importing.value = true
    const formData = new FormData()
    formData.append('har_file', importForm.value.file)
    formData.append('name', importForm.value.name)
    formData.append('resource_types', importForm.value.resource_types.join(','))
    if (importForm.value.host_replacement) {
      formData.append('host_replacement', importForm.value.host_replacement)
    }
    
    await scenarioApi.importHar(formData)
    ElMessage.success('导入成功')
    showImportDialog.value = false
    importForm.value = {
      name: '',
      resource_types: ['xhr', 'document'],
      host_replacement: '',
      file: null
    }
    fetchScenarios()
  } catch (error) {
    console.error('Import HAR error:', error)
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

const editScenario = (row) => {
  router.push(`/scenarios/${row.id}/edit`)
}

const copyScenario = async (row) => {
  try {
    await scenarioApi.copy(row.id)
    ElMessage.success('复制成功')
    fetchScenarios()
  } catch (error) {
    console.error('Copy scenario error:', error)
    ElMessage.error(error.message || '复制失败')
  }
}

const deleteScenario = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该场景吗？', '提示', { type: 'warning' })
    await scenarioApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchScenarios()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete scenario error:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const runTest = (row) => {
  currentScenario.value = row
  showRunDialog.value = true
}

const confirmRun = async () => {
  try {
    running.value = true
    // 创建报告参数
    const reportData = {
      scenario: currentScenario.value.id,
      name: `${currentScenario.value.name}_压测_${Date.now()}`,
      users: runForm.value.users,
      spawn_rate: runForm.value.spawn_rate,
      duration: runForm.value.duration
    }
    
    // 创建报告
    const reportResponse = await reportApi.create(reportData)
    // 然后运行压测
    await reportApi.run(reportResponse.id)
    
    ElMessage.success('压测已启动')
    showRunDialog.value = false
    router.push('/reports')
  } catch (error) {
    console.error('Run test error:', error)
    ElMessage.error(error.message || '启动压测失败')
  } finally {
    running.value = false
  }
}
</script>

<style scoped>
.scenarios-page {
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

.ml-2 {
  margin-left: 8px;
}
</style>
