<template>
  <div class="reports-page">
    <div class="page-header">
      <h2>报告管理</h2>
    </div>

    <el-card>
      <el-table :data="reports" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="报告名称" show-overflow-tooltip />
        <el-table-column prop="scenario_name" label="场景" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="users" label="并发数" width="100" />
        <el-table-column prop="duration" label="时长(秒)" width="100" />
        <el-table-column prop="success_rate" label="成功率" width="100">
          <template #default="{ row }">
            {{ row.success_rate?.toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="rps" label="RPS" width="100">
          <template #default="{ row }">
            {{ row.rps?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewReport(row)">查看</el-button>
            <el-button v-if="row.status === 'running'" link type="danger" @click="stopReport(row)">停止</el-button>
            <el-button link type="danger" @click="deleteReport(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { reportApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const reports = ref([])

// 调用 API 获取报告列表
onMounted(() => {
  fetchReports()
})

const fetchReports = async () => {
  try {
    loading.value = true
    const data = await reportApi.list()
    reports.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch reports:', error)
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const map = {
    'completed': 'success',
    'running': 'primary',
    'failed': 'danger',
    'pending': 'info',
    'stopped': 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'completed': '已完成',
    'running': '运行中',
    'failed': '失败',
    'pending': '待运行',
    'stopped': '已停止'
  }
  return map[status] || status
}

const viewReport = (row) => {
  router.push(`/reports/${row.id}`)
}

const stopReport = async (row) => {
  try {
    await ElMessageBox.confirm('确定要停止该压测吗？', '提示', { type: 'warning' })
    await reportApi.stop(row.id)
    ElMessage.success('已停止')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Stop report error:', error)
      ElMessage.error(error.message || '停止失败')
    }
  }
}

const deleteReport = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗？', '提示', { type: 'warning' })
    await reportApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete report error:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.reports-page {
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
</style>
