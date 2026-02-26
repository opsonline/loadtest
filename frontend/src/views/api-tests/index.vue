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
              <el-button type="primary" link @click="openCreateSuite">
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
                <el-button type="primary" @click="openCreateCase">
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
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" @click="runCase(row)">运行</el-button>
                <el-button link type="primary" @click="editCase(row)">编辑</el-button>
                <el-button link type="danger" @click="deleteCase(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card v-if="testResults.length > 0" class="mt-20">
          <template #header>
            <span>测试结果</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="result in testResults"
              :key="result.id"
              :type="result.status === 'passed' ? 'success' : 'danger'"
            >
              <h4>{{ result.test_case_name }} - {{ result.status === 'passed' ? '通过' : '失败' }}</h4>
              <p>状态码: {{ result.response_status }} | 响应时间: {{ result.response_time }}ms</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

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

    <el-dialog v-model="showSuiteDialog" :title="suiteForm.id ? '编辑套件' : '创建套件'" width="500px">
      <el-form :model="suiteForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="suiteForm.name" placeholder="输入套件名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" placeholder="输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSuiteDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSuite" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCaseDialog" :title="caseForm.id ? '编辑用例' : '创建用例'" width="700px">
      <el-form :model="caseForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="caseForm.name" placeholder="输入用例名称" />
        </el-form-item>
        <el-form-item label="方法" required>
          <el-select v-model="caseForm.method" style="width: 120px">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>
        <el-form-item label="URL" required>
          <el-input v-model="caseForm.url" placeholder="https://api.example.com/users" />
        </el-form-item>
        <el-form-item label="Headers">
          <el-input v-model="caseForm.headersText" type="textarea" :rows="3" placeholder='{"Content-Type": "application/json"}' />
        </el-form-item>
        <el-form-item label="Body">
          <el-input v-model="caseForm.body" type="textarea" :rows="5" placeholder="请求体" />
        </el-form-item>
        
        <el-divider>断言规则</el-divider>
        
        <div v-for="(assertion, index) in caseForm.assertions" :key="index" class="assertion-item">
          <el-form :model="assertion" label-width="80px">
            <el-row :gutter="10">
              <el-col :span="6">
                <el-select v-model="assertion.assertion_type" placeholder="断言类型" @change="onAssertionTypeChange(assertion)">
                  <el-option label="状态码" value="status_code" />
                  <el-option label="响应时间" value="response_time" />
                  <el-option label="JSON路径" value="json_path" />
                  <el-option label="正则匹配" value="regex" />
                  <el-option label="包含验证" value="contains" />
                  <el-option label="数值范围" value="numeric_range" />
                </el-select>
              </el-col>
              <el-col :span="6" v-if="assertion.assertion_type === 'status_code'">
                <el-input v-model="assertion.expected_value" placeholder="如: 200" />
              </el-col>
              <el-col :span="6" v-if="assertion.assertion_type === 'response_time'">
                <el-input v-model="assertion.expected_value" placeholder="最大响应时间(ms)" />
              </el-col>
              <el-col :span="6" v-if="['json_path', 'regex', 'contains'].includes(assertion.assertion_type)">
                <el-input v-model="assertion.target_path" :placeholder="getAssertionPlaceholder(assertion.assertion_type)" />
              </el-col>
              <el-col :span="6" v-if="['json_path', 'regex', 'contains'].includes(assertion.assertion_type)">
                <el-input v-model="assertion.expected_value" placeholder="期望值" />
              </el-col>
              <el-col :span="6" v-if="assertion.assertion_type === 'numeric_range'">
                <el-input v-model="assertion.target_path" placeholder="JSON路径" />
              </el-col>
              <el-col :span="3" v-if="assertion.assertion_type === 'numeric_range'">
                <el-input v-model="assertion.min_value" placeholder="最小值" />
              </el-col>
              <el-col :span="3" v-if="assertion.assertion_type === 'numeric_range'">
                <el-input v-model="assertion.max_value" placeholder="最大值" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" icon="Delete" circle @click="removeAssertion(index)" />
              </el-col>
            </el-row>
          </el-form>
        </div>
        
        <el-button type="primary" link @click="addAssertion" style="margin-top: 10px;">
          <el-icon><Plus /></el-icon>添加断言
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="showCaseDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCase" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Position, VideoPlay, Delete } from '@element-plus/icons-vue'
import { apiTestApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const suites = ref([])
const testCases = ref([])
const testResults = ref([])
const activeSuite = ref('')
const currentSuite = ref(null)
const showSingleTest = ref(false)
const showSuiteDialog = ref(false)
const showCaseDialog = ref(false)

const singleTestForm = ref({
  method: 'GET',
  url: '',
  headers: '',
  body: ''
})

const singleTestResult = ref(null)

const suiteForm = ref({
  id: null,
  name: '',
  description: ''
})

const caseForm = ref({
  id: null,
  name: '',
  method: 'GET',
  url: '',
  headersText: '',
  body: '',
  assertions: []
})

const assertionTypes = {
  status_code: '状态码',
  response_time: '响应时间',
  json_path: 'JSON路径',
  regex: '正则匹配',
  contains: '包含验证',
  numeric_range: '数值范围'
}

onMounted(() => {
  fetchSuites()
})

const fetchSuites = async () => {
  try {
    const data = await apiTestApi.listSuites()
    suites.value = data.results || data || []
    if (suites.value.length > 0) {
      selectSuite(suites.value[0].id)
    }
  } catch (error) {
    console.error('Failed to fetch suites:', error)
    ElMessage.error('获取测试套件失败')
  }
}

const selectSuite = (suiteId) => {
  activeSuite.value = suiteId
  currentSuite.value = suites.value.find(s => s.id === suiteId)
  fetchTestCases(suiteId)
}

const fetchTestCases = async (suiteId) => {
  loading.value = true
  try {
    const data = await apiTestApi.listCases(suiteId)
    testCases.value = data.results || data || []
  } catch (error) {
    console.error('Failed to fetch test cases:', error)
    ElMessage.error('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const getMethodType = (method) => {
  const map = { 'GET': 'success', 'POST': 'primary', 'PUT': 'warning', 'DELETE': 'danger', 'PATCH': 'info' }
  return map[method] || ''
}

const getAssertionPlaceholder = (type) => {
  const map = {
    json_path: '$.data.id',
    regex: '正则表达式',
    contains: '包含的文本'
  }
  return map[type] || ''
}

const addAssertion = () => {
  caseForm.value.assertions.push({
    name: '',
    assertion_type: 'status_code',
    target_path: '',
    expected_value: '',
    operator: 'eq',
    min_value: null,
    max_value: null
  })
}

const removeAssertion = (index) => {
  caseForm.value.assertions.splice(index, 1)
}

const onAssertionTypeChange = (assertion) => {
  assertion.target_path = ''
  assertion.expected_value = ''
  assertion.operator = 'eq'
  assertion.min_value = null
  assertion.max_value = null
}

const openCreateSuite = () => {
  suiteForm.value = { id: null, name: '', description: '' }
  showSuiteDialog.value = true
}

const openCreateCase = () => {
  caseForm.value = { id: null, name: '', method: 'GET', url: '', headersText: '', body: '' }
  showCaseDialog.value = true
}

const saveSuite = async () => {
  if (!suiteForm.value.name) {
    ElMessage.warning('请输入套件名称')
    return
  }
  
  saving.value = true
  try {
    if (suiteForm.value.id) {
      await apiTestApi.updateSuite(suiteForm.value.id, suiteForm.value)
      ElMessage.success('更新成功')
    } else {
      await apiTestApi.createSuite(suiteForm.value)
      ElMessage.success('创建成功')
    }
    showSuiteDialog.value = false
    fetchSuites()
  } catch (error) {
    console.error('Failed to save suite:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const saveCase = async () => {
  if (!caseForm.value.name || !caseForm.value.url) {
    ElMessage.warning('请填写必要字段')
    return
  }
  
  saving.value = true
  try {
    let headers = {}
    try {
      if (caseForm.value.headersText) {
        headers = JSON.parse(caseForm.value.headersText)
      }
    } catch (e) {
      ElMessage.warning('Headers 格式不正确')
      saving.value = false
      return
    }
    
    const data = {
      name: caseForm.value.name,
      method: caseForm.value.method,
      url: caseForm.value.url,
      headers: headers,
      body: caseForm.value.body || null,
      assertions: caseForm.value.assertions.filter(a => a.assertion_type)
    }
    
    if (caseForm.value.id) {
      await apiTestApi.updateCase(caseForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await apiTestApi.createCase(currentSuite.value.id, data)
      ElMessage.success('创建成功')
    }
    showCaseDialog.value = false
    fetchTestCases(activeSuite.value)
  } catch (error) {
    console.error('Failed to save case:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const executeSingleTest = async () => {
  if (!singleTestForm.value.url) {
    ElMessage.warning('请输入URL')
    return
  }
  
  testing.value = true
  singleTestResult.value = null
  
  try {
    let headers = {}
    try {
      if (singleTestForm.value.headers) {
        headers = JSON.parse(singleTestForm.value.headers)
      }
    } catch (e) {
      ElMessage.warning('Headers 格式不正确')
      testing.value = false
      return
    }
    
    const result = await apiTestApi.executeRequest({
      method: singleTestForm.value.method,
      url: singleTestForm.value.url,
      headers: headers,
      body: singleTestForm.value.body || null,
      assertions: []
    })
    
    singleTestResult.value = result
  } catch (error) {
    console.error('Failed to execute test:', error)
    ElMessage.error(error.message || '执行失败')
  } finally {
    testing.value = false
  }
}

const runCase = async (row) => {
  try {
    const result = await apiTestApi.execute({ test_case_id: row.id })
    if (result.status === 'passed') {
      ElMessage.success('测试通过')
    } else {
      ElMessage.error('测试失败')
    }
    
    testResults.value = [result, ...testResults.value].slice(0, 10)
  } catch (error) {
    console.error('Failed to run case:', error)
    ElMessage.error(error.message || '运行失败')
  }
}

const runSuite = async () => {
  if (!currentSuite.value) return
  
  try {
    const results = await apiTestApi.execute({ suite_id: currentSuite.value.id })
    ElMessage.success('套件测试完成')
    
    if (Array.isArray(results)) {
      testResults.value = [...results, ...testResults.value].slice(0, 10)
    }
  } catch (error) {
    console.error('Failed to run suite:', error)
    ElMessage.error(error.message || '运行失败')
  }
}

const editCase = async (row) => {
  caseForm.value = {
    id: row.id,
    name: row.name,
    method: row.method,
    url: row.url,
    headersText: row.headers ? JSON.stringify(row.headers, null, 2) : '',
    body: row.body || '',
    assertions: row.assertions || []
  }
  showCaseDialog.value = true
}

const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', { type: 'warning' })
    await apiTestApi.deleteCase(row.id)
    ElMessage.success('删除成功')
    fetchTestCases(activeSuite.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete case:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
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

.assertion-item {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f9f9f9;
}
</style>