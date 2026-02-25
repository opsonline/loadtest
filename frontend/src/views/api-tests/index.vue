<template>
  <div class="api-tests-page">
    <div class="page-header">
      <h2>接口测试</h2>
      <el-button type="primary" @click="showSingleTest = true">
        <el-icon><Position /></el-icon>快速测试
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>测试套件</span>
              <el-button type="primary" link @click="showCreateSuite = true">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <el-menu :default-active="activeSuite" @select="selectSuite">
            <el-menu-item v-for="suite in suites" :key="suite.id" :index="suite.id">
              {{ suite.name }}
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ currentSuite?.name || '测试用例' }}</span>
              <div v-if="currentSuite">
                <el-button type="primary" @click="showCreateCase = true">
                  <el-icon><Plus /></el-icon>添加用例
                </el-button>
                <el-button type="success" @click="runSuite">
                  <el-icon><VideoPlay /></el-icon>运行套件
                </el-button>
              </div>
            </div>
          </template>

          <el-table :data="testCases" v-loading="loading" style="width: 100%">
            <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
            <el-table-column prop="method" label="方法" width="80">
              <template #default="{ row }">
                <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="URL" show-overflow-tooltip />
            <el-table-column prop="assertion_count" label="断言数" width="100" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" @click="runCase(row)">运行</el-button>
                <el-button link type="primary" @click="editCase(row)">编辑</el-button>
                <el-button link type="danger" @click="deleteCase(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 测试结果 -->
        <el-card v-if="testResults.length > 0" class="mt-20">
          <template #header>
            <span>测试结果</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="result in testResults"
              :key="result.id"
              :type="result.status === 'passed' ? 'success' : 'danger'"
              :icon="result.status === 'passed' ? 'Check' : 'Close'"
            >
              <h4>{{ result.test_case_name }} - {{ result.status === 'passed' ? '通过' : '失败' }}</h4>
              <p>状态码: {{ result.response_status }} | 响应时间: {{ result.response_time }}ms</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速测试对话框 -->
    <el-dialog v-model="showSingleTest" title="快速测试" width="800px">
      <el-form :model="singleTestForm" label-width="80px">
        <el-form-item label="URL">
          <el-input v-model="singleTestForm.url" placeholder="https://api.example.com/users">
            <template #prepend>
              <el-select v-model="singleTestForm.method" style="width: 100px">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="Headers">
          <el-input v-model="singleTestForm.headers" type="textarea" placeholder='{"Content-Type": "application/json"}' />
        </el-form-item>
        <el-form-item label="Body">
          <el-input v-model="singleTestForm.body" type="textarea" :rows="5" placeholder="请求体" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSingleTest = false">取消</el-button>
        <el-button type="primary" @click="executeSingleTest" :loading="testing">发送请求</el-button>
      </template>

      <!-- 响应结果 -->
      <div v-if="singleTestResult" class="response-section">
        <el-divider />
        <h4>响应结果</h4>
        <div class="response-info">
          <el-tag :type="singleTestResult.status === 'passed' ? 'success' : 'danger'">
            {{ singleTestResult.status === 'passed' ? '成功' : '失败' }}
          </el-tag>
          <span>状态码: {{ singleTestResult.response_status }}</span>
          <span>响应时间: {{ singleTestResult.response_time }}ms</span>
        </div>
        <el-input v-model="singleTestResult.response_body" type="textarea" :rows="10" readonly />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Position, VideoPlay } from '@element-plus/icons-vue'

const loading = ref(false)
const suites = ref([])
const testCases = ref([])
const testResults = ref([])
const activeSuite = ref('')
const currentSuite = ref(null)
const showSingleTest = ref(false)
const showCreateSuite = ref(false)
const showCreateCase = ref(false)
const testing = ref(false)

const singleTestForm = ref({
  method: 'GET',
  url: '',
  headers: '',
  body: ''
})

const singleTestResult = ref(null)

// TODO: 调用 API 获取数据
onMounted(() => {
  fetchSuites()
})

const fetchSuites = () => {
  // 模拟数据
  suites.value = [
    { id: '1', name: '用户模块测试' },
    { id: '2', name: '订单模块测试' }
  ]
}

const selectSuite = (suiteId) => {
  activeSuite.value = suiteId
  currentSuite.value = suites.value.find(s => s.id === suiteId)
  fetchTestCases(suiteId)
}

const fetchTestCases = (suiteId) => {
  loading.value = true
  // 模拟数据
  setTimeout(() => {
    testCases.value = [
      { id: '1', name: '获取用户列表', method: 'GET', url: '/api/users', assertion_count: 2 },
      { id: '2', name: '创建用户', method: 'POST', url: '/api/users', assertion_count: 3 }
    ]
    loading.value = false
  }, 300)
}

const getMethodType = (method) => {
  const map = { 'GET': 'success', 'POST': 'primary', 'PUT': 'warning', 'DELETE': 'danger', 'PATCH': 'info' }
  return map[method] || ''
}

const executeSingleTest = async () => {
  testing.value = true
  // TODO: 调用 API 执行测试
  setTimeout(() => {
    singleTestResult.value = {
      status: 'passed',
      response_status: 200,
      response_time: 125,
      response_body: JSON.stringify({ id: 1, name: 'Test User' }, null, 2)
    }
    testing.value = false
  }, 1000)
}

const runCase = async (row) => {
  // TODO: 调用 API 运行单个用例
  ElMessage.success('测试完成')
}

const runSuite = async () => {
  // TODO: 调用 API 运行整个套件
  ElMessage.success('套件测试完成')
}

const editCase = (row) => {
  // 编辑用例
}

const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', { type: 'warning' })
    // TODO: 调用 API 删除
    ElMessage.success('删除成功')
    fetchTestCases(activeSuite.value)
  } catch {}
}
</script>

<style scoped>
.api-tests-page {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mt-20 {
  margin-top: 20px;
}

.response-section {
  margin-top: 20px;
}

.response-info {
  margin: 10px 0;
  display: flex;
  gap: 15px;
  align-items: center;
}
</style>
