<template>
  <div class="datasources-page">
    <div class="page-header">
      <h2>数据源管理</h2>
      <div class="header-actions">
        <el-button @click="exportDatasources" :disabled="datasources.length === 0">
          <el-icon><Download /></el-icon>导出配置
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建数据源
        </el-button>
      </div>
    </div>

    <el-card>
      <el-table :data="datasources" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="数据源名称" show-overflow-tooltip />
        <el-table-column prop="source_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getTypeText(row.source_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="数据量" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="previewDataSource(row)">预览</el-button>
            <el-button link type="primary" @click="testConnection(row)">测试</el-button>
            <el-button link type="primary" @click="editDatasource(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteDatasource(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑数据源对话框 -->
    <el-dialog v-model="showCreateDialog" :title="isEdit ? '编辑数据源' : '创建数据源'" width="600px">
      <el-form :model="datasourceForm" label-width="120px">
        <el-form-item label="数据源名称">
          <el-input v-model="datasourceForm.name" placeholder="输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据源类型">
          <el-select v-model="datasourceForm.source_type" placeholder="选择类型" style="width: 100%">
            <el-option label="CSV文件" value="csv" />
            <el-option label="JSON文件" value="json" />
            <el-option label="MySQL" value="mysql" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MongoDB" value="mongodb" />
            <el-option label="Redis" value="redis" />
            <el-option label="Python脚本" value="python" />
          </el-select>
        </el-form-item>

        <!-- 文件类型配置 -->
        <template v-if="['csv', 'json'].includes(datasourceForm.source_type)">
          <el-form-item label="文件上传">
            <el-upload
              drag
              action=""
              :auto-upload="false"
              :on-change="handleFileChange"
              accept=".csv,.json"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
            </el-upload>
          </el-form-item>
          <el-form-item label="编码" v-if="datasourceForm.source_type === 'csv'">
            <el-input v-model="datasourceForm.file_encoding" placeholder="utf-8" />
          </el-form-item>
          <el-form-item label="分隔符" v-if="datasourceForm.source_type === 'csv'">
            <el-input v-model="datasourceForm.csv_delimiter" placeholder="," />
          </el-form-item>
        </template>

        <!-- 数据库类型配置 -->
        <template v-if="['mysql', 'postgresql', 'mongodb'].includes(datasourceForm.source_type)">
          <el-form-item label="主机">
            <el-input v-model="datasourceForm.db_host" placeholder="localhost" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number v-model="datasourceForm.db_port" :min="1" :max="65535" style="width: 100%" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="datasourceForm.db_user" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="datasourceForm.db_password" type="password" />
          </el-form-item>
          <el-form-item label="数据库">
            <el-input v-model="datasourceForm.db_name" />
          </el-form-item>
          <el-form-item label="查询语句" v-if="datasourceForm.source_type !== 'mongodb'">
            <el-input v-model="datasourceForm.db_query" type="textarea" placeholder="SELECT * FROM table" />
          </el-form-item>
          <el-form-item label="集合" v-if="datasourceForm.source_type === 'mongodb'">
            <el-input v-model="datasourceForm.db_collection" />
          </el-form-item>
        </template>

        <!-- Redis配置 -->
        <template v-if="datasourceForm.source_type === 'redis'">
          <el-form-item label="主机">
            <el-input v-model="datasourceForm.db_host" placeholder="localhost" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number v-model="datasourceForm.db_port" :min="1" :max="65535" placeholder="6379" style="width: 100%" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="datasourceForm.db_password" type="password" />
          </el-form-item>
          <el-form-item label="Key">
            <el-input v-model="datasourceForm.redis_key" placeholder="user:*" />
          </el-form-item>
        </template>

        <!-- Python脚本 -->
        <template v-if="datasourceForm.source_type === 'python'">
          <el-form-item label="Python脚本">
            <el-input v-model="datasourceForm.python_script" type="textarea" :rows="10" 
              placeholder="# 定义一个名为 data 的变量&#10;data = [&#10;    {'id': 1, 'name': 'test1'},&#10;    {'id': 2, 'name': 'test2'}&#10;]" />
          </el-form-item>
        </template>

        <el-form-item label="描述">
          <el-input v-model="datasourceForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDatasource" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 数据预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="数据预览" width="800px">
      <el-table :data="previewData" style="width: 100%" max-height="400">
        <el-table-column v-for="key in previewKeys" :key="key" :prop="key" :label="key" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { datasourceApi } from '@/api'

const loading = ref(false)
const datasources = ref([])
const showCreateDialog = ref(false)
const showPreviewDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentDatasourceId = ref(null)
const previewData = ref([])
const previewKeys = ref([])

const datasourceForm = ref({
  name: '',
  source_type: 'csv',
  file_path: '',
  file_encoding: 'utf-8',
  csv_delimiter: ',',
  db_host: '',
  db_port: null,
  db_user: '',
  db_password: '',
  db_name: '',
  db_query: '',
  db_collection: '',
  redis_key: '',
  python_script: '',
  description: ''
})

// TODO: 调用 API 获取数据源列表
onMounted(() => {
  fetchDatasources()
})

const fetchDatasources = async () => {
  try {
    loading.value = true
    const data = await datasourceApi.list()
    datasources.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch datasources:', error)
    ElMessage.error('获取数据源列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getTypeText = (type) => {
  const map = {
    'csv': 'CSV', 'json': 'JSON', 'mysql': 'MySQL',
    'postgresql': 'PostgreSQL', 'mongodb': 'MongoDB',
    'redis': 'Redis', 'python': 'Python'
  }
  return map[type] || type
}

const handleFileChange = (file) => {
  // 处理文件上传
}

const saveDatasource = async () => {
  if (!datasourceForm.value.name) {
    ElMessage.warning('请输入数据源名称')
    return
  }
  
  saving.value = true
  try {
    if (isEdit.value) {
      await datasourceApi.update(currentDatasourceId.value, datasourceForm.value)
      ElMessage.success('更新成功')
    } else {
      await datasourceApi.create(datasourceForm.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    resetForm()
    fetchDatasources()
  } catch (error) {
    console.error('Save datasource error:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const editDatasource = async (row) => {
  isEdit.value = true
  currentDatasourceId.value = row.id
  try {
    const detail = await datasourceApi.get(row.id)
    datasourceForm.value = { ...detail }
    showCreateDialog.value = true
  } catch (error) {
    console.error('Failed to get datasource detail:', error)
    ElMessage.error('获取数据源详情失败')
  }
}

const resetForm = () => {
  datasourceForm.value = {
    name: '',
    source_type: 'csv',
    file_path: '',
    file_encoding: 'utf-8',
    csv_delimiter: ',',
    db_host: '',
    db_port: null,
    db_user: '',
    db_password: '',
    db_name: '',
    db_query: '',
    db_collection: '',
    redis_key: '',
    python_script: '',
    description: ''
  }
  currentDatasourceId.value = null
  isEdit.value = false
}

const deleteDatasource = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据源吗？', '提示', { type: 'warning' })
    await datasourceApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchDatasources()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete datasource error:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const testConnection = async (row) => {
  try {
    await datasourceApi.test(row.id)
    ElMessage.success('连接成功')
  } catch (error) {
    console.error('Test connection error:', error)
    ElMessage.error(error.message || '连接失败')
  }
}

const previewDataSource = async (row) => {
  try {
    const data = await datasourceApi.preview(row.id)
    if (data && data.length > 0) {
      previewData.value = data.slice(0, 10)
      previewKeys.value = Object.keys(data[0])
    } else {
      previewData.value = []
      previewKeys.value = []
    }
    showPreviewDialog.value = true
  } catch (error) {
    console.error('Preview data error:', error)
    ElMessage.error(error.message || '预览失败')
  }
}

const exportDatasources = async () => {
  if (datasources.value.length === 0) {
    ElMessage.warning('没有可导出的数据源')
    return
  }
  
  try {
    const exportData = datasources.value.map(ds => ({
      name: ds.name,
      source_type: ds.source_type,
      description: ds.description,
      // 不导出敏感信息如密码
      config: {
        file_path: ds.file_path,
        db_host: ds.db_host,
        db_port: ds.db_port,
        db_user: ds.db_user,
        db_name: ds.db_name,
        db_query: ds.db_query,
        db_collection: ds.db_collection,
        redis_key: ds.redis_key,
        file_encoding: ds.file_encoding,
        csv_delimiter: ds.csv_delimiter
      }
    }))
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `datasources_export_${dayjs().format('YYYYMMDD_HHmmss')}.json`
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
.datasources-page {
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
</style>
