<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon blue">
            <el-icon><List /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.scenario_count }}</div>
            <div class="stat-label">场景数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon green">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.report_count }}</div>
            <div class="stat-label">报告数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon orange">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.datasource_count }}</div>
            <div class="stat-label">数据源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon purple">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.test_suite_count }}</div>
            <div class="stat-label">测试套件</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近压测报告</span>
          </template>
          <el-table :data="recentReports" style="width: 100%">
            <el-table-column prop="name" label="报告名称" show-overflow-tooltip />
            <el-table-column prop="scenario" label="场景" width="120">
              <template #default="{ row }">
                {{ typeof row.scenario === 'object' ? row.scenario?.name : row.scenario }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/scenarios/create')">
              <el-icon><Plus /></el-icon>创建场景
            </el-button>
            <el-button @click="$router.push('/scenarios')">
              <el-icon><List /></el-icon>场景管理
            </el-button>
            <el-button @click="$router.push('/reports')">
              <el-icon><Document /></el-icon>查看报告
            </el-button>
            <el-button @click="$router.push('/api-tests')">
              <el-icon><Connection /></el-icon>接口测试
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { List, Document, DataLine, Connection, Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { scenarioApi, reportApi, datasourceApi, apiTestApi } from '@/api'

const stats = ref({
  scenario_count: 0,
  report_count: 0,
  datasource_count: 0,
  test_suite_count: 0
})

const recentReports = ref([])

onMounted(async () => {
  try {
    // 调用各API获取统计数据
    const [scenariosRes, reportsRes, datasourcesRes, apiTestsRes] = await Promise.all([
      scenarioApi.list({ page_size: 1000 }),
      reportApi.list({ page_size: 1000 }),
      datasourceApi.list({ page_size: 1000 }),
      apiTestApi.listSuites({ page_size: 1000 })
    ])
    
    stats.value = {
      scenario_count: scenariosRes.count || 0,
      report_count: reportsRes.count || 0,
      datasource_count: datasourcesRes.count || 0,
      test_suite_count: apiTestsRes.count || 0
    }
    
    // 获取最近5条报告
    const recentRes = await reportApi.list({ page_size: 5 })
    recentReports.value = recentRes.results || recentRes || []
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    // 使用空数据
    stats.value = {
      scenario_count: 0,
      report_count: 0,
      datasource_count: 0,
      test_suite_count: 0
    }
    recentReports.value = []
  }
})

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

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 15px;
}

.stat-icon.blue {
  background: #e6f7ff;
  color: #1890ff;
}

.stat-icon.green {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.orange {
  background: #fff7e6;
  color: #fa8c16;
}

.stat-icon.purple {
  background: #f9f0ff;
  color: #722ed1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.mt-20 {
  margin-top: 20px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.quick-actions .el-button {
  flex: 1;
  min-width: 120px;
}
</style>
