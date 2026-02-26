<template>
  <div class="report-detail" v-if="report">
    <div class="page-header">
      <h2>{{ report.name }}</h2>
       <div>
         <el-button type="primary" @click="exportReport('pdf')" style="margin-right: 10px;">
           导出PDF
         </el-button>
         <el-button type="success" @click="exportReport('excel')">
           导出Excel
         </el-button>
         <el-tag :type="getStatusType(report.status)" style="margin-left: 10px;">
           {{ getStatusText(report.status) }}
         </el-tag>
       </div>
     </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ report.total_requests }}</div>
          <div class="stat-label">总请求数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ report.success_rate?.toFixed(2) }}%</div>
          <div class="stat-label">成功率</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ report.rps?.toFixed(2) }}</div>
          <div class="stat-label">RPS</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ report.avg_response_time?.toFixed(2) }}ms</div>
          <div class="stat-label">平均响应时间</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="mt-20">
      <template #header>
        <span>响应时间分布</span>
      </template>
      <div class="response-time-stats">
        <div class="stat-item">
          <div class="stat-label">最小</div>
          <div class="stat-value">{{ report.min_response_time }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">P50</div>
          <div class="stat-value">{{ report.p50_response_time }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">P90</div>
          <div class="stat-value">{{ report.p90_response_time }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">P95</div>
          <div class="stat-value">{{ report.p95_response_time }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">P99</div>
          <div class="stat-value">{{ report.p99_response_time }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">最大</div>
          <div class="stat-value">{{ report.max_response_time }}ms</div>
        </div>
      </div>
    </el-card>

    <!-- 实时监控图表 -->
    <el-card class="mt-20" v-if="report?.status === 'running' || isLiveUpdatesEnabled">
      <template #header>
        <div class="chart-header">
          <span>实时监控</span>
          <el-tag :type="isLiveUpdatesEnabled ? 'success' : 'danger'">
            {{ isLiveUpdatesEnabled ? '连接中' : '未连接' }}
          </el-tag>
        </div>
      </template>
      <div class="realtime-stats">
        <div class="stat-item">
          <div class="stat-label">RPS</div>
          <div class="stat-value">{{ report?.rps?.toFixed(2) || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">平均响应时间</div>
          <div class="stat-value">{{ report?.avg_response_time?.toFixed(2) || 0 }}ms</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">总请求数</div>
          <div class="stat-value">{{ report?.total_requests || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">成功率</div>
          <div class="stat-value">{{ report?.success_rate?.toFixed(2) || 0 }}%</div>
        </div>
      </div>
      
      <!-- RPS 图表 -->
      <div id="rps-chart" style="height: 300px; margin-top: 20px;"></div>
      
      <!-- 响应时间图表 -->
      <div id="response-time-chart" style="height: 300px; margin-top: 20px;"></div>
    </el-card>
    
    <!-- 统计分析图表 -->
    <el-card class="mt-20" v-if="report">
      <template #header>
        <span>统计分析</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <!-- 成功率饼图 -->
          <div id="success-rate-pie" style="height: 300px;"></div>
        </el-col>
        <el-col :span="12">
          <!-- 响应时间分布饼图 -->
          <div id="response-time-distribution" style="height: 300px;"></div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <!-- 请求响应时间柱状图 -->
          <div id="request-response-bar" style="height: 400px;"></div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="mt-20">
      <template #header>
        <span>请求统计</span>
      </template>
      <el-table :data="requestStats" style="width: 100%">
        <el-table-column prop="request_name" label="请求名称" />
        <el-table-column prop="method" label="方法" width="80" />
        <el-table-column prop="num_requests" label="请求数" width="100" />
        <el-table-column prop="avg_response_time" label="平均响应时间" width="120">
          <template #default="{ row }">{{ row.avg_response_time?.toFixed(2) }}ms</template>
        </el-table-column>
        <el-table-column prop="p95_response_time" label="P95" width="100">
          <template #default="{ row }">{{ row.p95_response_time?.toFixed(2) }}ms</template>
        </el-table-column>
        <el-table-column prop="p99_response_time" label="P99" width="100">
          <template #default="{ row }">{{ row.p99_response_time?.toFixed(2) }}ms</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { reportApi, websocketUtils } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { reportExportApi } from '@/api'

const route = useRoute()
const report = ref(null)
const requestStats = ref([])
const wsConnection = ref(null)
const statsUpdate = ref(null)
const isLiveUpdatesEnabled = ref(false)

const fetchReport = async () => {
  try {
    const data = await reportApi.detail(route.params.id)
    report.value = data
    
    // 获取请求统计
    if (data.id) {
      try {
        const statsData = await reportApi.stats(data.id)
        requestStats.value = Object.entries(statsData.requests || {}).map(([name, stat]) => ({
          request_name: name,
          method: stat.method || 'GET',
          num_requests: stat.num_requests || 0,
          num_failures: stat.num_failures || 0,
          avg_response_time: stat.avg_response_time || 0,
          p95_response_time: stat.p95 || 0,
          p99_response_time: stat.p99 || 0
        }))
      } catch (e) {
        console.error('Failed to fetch stats:', e)
      }
    }
    
    // 如果报告正在运行，启动WebSocket连接
    if (data.status === 'running') {
      connectWebSocket()
    }
  } catch (error) {
    console.error('Failed to fetch report:', error)
    ElMessage.error('获取报告详情失败')
  }
}

const connectWebSocket = () => {
  if (wsConnection.value) {
    wsConnection.value.close()
  }
  
  try {
    wsConnection.value = websocketUtils.connect(report.value.id)
    isLiveUpdatesEnabled.value = true
    
    wsConnection.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'load_test_update') {
        updateReportWithLiveStats(data)
        updateChartData(
          data.timestamp,
          data.stats?.rps || 0,
          data.stats?.avg_response_time || 0
        )
      }
    }
    
    wsConnection.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      isLiveUpdatesEnabled.value = false
    }
    
    wsConnection.value.onclose = () => {
      isLiveUpdatesEnabled.value = false
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
    isLiveUpdatesEnabled.value = false
  }
}

// 图表实例
const rpsChart = ref(null)
const responseTimeChart = ref(null)
const successRatePieChart = ref(null)
const responseTimeDistributionChart = ref(null)
const requestResponseBarChart = ref(null)

// 图表数据
const chartData = ref({
  timestamps: [],
  rpsData: [],
  responseTimeData: []
})

onMounted(() => {
  fetchReport()
  // 初始化图表
  initCharts()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 监听窗口大小变化，调整图表尺寸
const resizeObserver = ref(null)

const exportReport = async (type) => {
  try {
    if (type === 'pdf') {
      await reportExportApi.exportPdf(route.params.id)
    } else if (type === 'excel') {
      await reportExportApi.exportExcel(route.params.id)
    }
    ElMessage.success(`报告导出成功`)
  } catch (error) {
    console.error(`导出${type}失败:`, error)
    ElMessage.error(`报告导出失败: ${error.message}`)
  }
}

onUnmounted(() => {
  // 组件卸载时断开WebSocket连接
  if (wsConnection.value) {
    wsConnection.value.close()
  }
  // 销毁图表
  if (rpsChart.value) {
    rpsChart.value.dispose()
  }
  if (responseTimeChart.value) {
    responseTimeChart.value.dispose()
  }
  if (successRatePieChart.value) {
    successRatePieChart.value.dispose()
  }
  if (responseTimeDistributionChart.value) {
    responseTimeDistributionChart.value.dispose()
  }
  if (requestResponseBarChart.value) {
    requestResponseBarChart.value.dispose()
  }
  // 移除事件监听器
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (rpsChart.value) {
    rpsChart.value.resize()
  }
  if (responseTimeChart.value) {
    responseTimeChart.value.resize()
  }
  if (successRatePieChart.value) {
    successRatePieChart.value.resize()
  }
  if (responseTimeDistributionChart.value) {
    responseTimeDistributionChart.value.resize()
  }
  if (requestResponseBarChart.value) {
    requestResponseBarChart.value.resize()
  }
}

// 更新统计图表
const updateStatisticalCharts = () => {
  if (report.value && requestStats.value.length > 0) {
    // 更新成功率饼图
    if (successRatePieChart.value) {
      // 计算成功和失败的请求数量
      const totalRequests = requestStats.value.reduce((sum, stat) => sum + (stat.num_requests || 0), 0)
      const totalFailures = requestStats.value.reduce((sum, stat) => sum + (stat.num_failures || 0), 0)
      const successfulRequests = totalRequests - totalFailures
      
      const pieData = [
        { value: successfulRequests, name: '成功请求', itemStyle: { color: '#52c41a' } },
        { value: totalFailures, name: '失败请求', itemStyle: { color: '#ff4d4f' } }
      ]
      
      successRatePieChart.value.setOption({
        series: [{
          data: pieData
        }]
      })
    }
    
    // 更新响应时间分布饼图
    if (responseTimeDistributionChart.value) {
      const distributionData = [
        { value: report.value.p50_response_time || 0, name: 'P50响应时间' },
        { value: report.value.p90_response_time || 0, name: 'P90响应时间' },
        { value: report.value.p95_response_time || 0, name: 'P95响应时间' },
        { value: report.value.p99_response_time || 0, name: 'P99响应时间' }
      ]
      
      responseTimeDistributionChart.value.setOption({
        series: [{
          data: distributionData
        }]
      })
    }
    
    // 更新请求响应时间柱状图
    if (requestResponseBarChart.value) {
      const requestNames = requestStats.value.map(stat => stat.request_name)
      const avgResponseTimes = requestStats.value.map(stat => stat.avg_response_time)
      const p95ResponseTimes = requestStats.value.map(stat => stat.p95_response_time)
      const p99ResponseTimes = requestStats.value.map(stat => stat.p99_response_time)
      
      requestResponseBarChart.value.setOption({
        xAxis: {
          data: requestNames
        },
        series: [
          {
            name: '平均响应时间',
            data: avgResponseTimes
          },
          {
            name: 'P95响应时间',
            data: p95ResponseTimes
          },
          {
            name: 'P99响应时间',
            data: p99ResponseTimes
          }
        ]
      })
    }
  }
}

// 当报告数据变更时，更新统计图表
watch(report, () => {
  updateStatisticalCharts()
}, { deep: true })

watch(requestStats, () => {
  updateStatisticalCharts()
}, { deep: true })

const initCharts = () => {
  // 初始化RPS图表
  rpsChart.value = echarts.init(document.getElementById('rps-chart'))
  rpsChart.value.setOption({
    title: {
      text: 'RPS 实时趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      name: 'RPS'
    },
    series: [{
      name: 'RPS',
      type: 'line',
      smooth: true,
      data: [],
      areaStyle: {}
    }]
  })
  
  // 初始化响应时间图表
  responseTimeChart.value = echarts.init(document.getElementById('response-time-chart'))
  responseTimeChart.value.setOption({
    title: {
      text: '平均响应时间趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      name: '响应时间 (ms)'
    },
    series: [{
      name: '响应时间',
      type: 'line',
      smooth: true,
      data: [],
      areaStyle: {}
    }]
  })
  
  // 初始化成功率饼图
  successRatePieChart.value = echarts.init(document.getElementById('success-rate-pie'))
  successRatePieChart.value.setOption({
    title: {
      text: '请求成功率',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '成功率',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '18',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: []
    }]
  })
  
  // 初始化响应时间分布饼图
  responseTimeDistributionChart.value = echarts.init(document.getElementById('response-time-distribution'))
  responseTimeDistributionChart.value.setOption({
    title: {
      text: '响应时间分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '响应时间分布',
      type: 'pie',
      radius: ['40%', '70%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: []
    }]
  })
  
  // 初始化请求响应时间柱状图
  requestResponseBarChart.value = echarts.init(document.getElementById('request-response-bar'))
  requestResponseBarChart.value.setOption({
    title: {
      text: '各请求响应时间对比'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['平均响应时间', 'P95响应时间', 'P99响应时间']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间 (ms)'
    },
    series: [
      {
        name: '平均响应时间',
        type: 'bar',
        data: []
      },
      {
        name: 'P95响应时间',
        type: 'bar',
        data: []
      },
      {
        name: 'P99响应时间',
        type: 'bar',
        data: []
      }
    ]
  })
}

const updateCharts = () => {
  if (rpsChart.value) {
    rpsChart.value.setOption({
      xAxis: {
        data: chartData.value.timestamps
      },
      series: [{
        data: chartData.value.rpsData
      }]
    })
  }
  
  if (responseTimeChart.value) {
    responseTimeChart.value.setOption({
      xAxis: {
        data: chartData.value.timestamps
      },
      series: [{
        data: chartData.value.responseTimeData
      }]
    })
  }
}

const updateChartData = (timestamp, rps, responseTime) => {
  // 限制数据点数量，避免图表过于拥挤
  if (chartData.value.timestamps.length >= 50) {
    chartData.value.timestamps.shift()
    chartData.value.rpsData.shift()
    chartData.value.responseTimeData.shift()
  }
  
  chartData.value.timestamps.push(timestamp.slice(-8)) // 显示时间HH:mm:ss的后8位
  chartData.value.rpsData.push(rps)
  chartData.value.responseTimeData.push(responseTime)
  
  updateCharts()
}

const updateReportWithLiveStats = (stats) => {
  // 更新报告的实时统计数据
  if (stats.history && stats.history.length > 0) {
    const latest = stats.history[stats.history.length - 1]
    report.value.rps = latest.rps
    report.value.avg_response_time = latest.avg_response_time
  }
  
  if (stats.requests) {
    let totalRequests = 0
    let totalFailures = 0
    let totalTime = 0
    let requestCount = 0
    
    Object.values(stats.requests).forEach(requestStat => {
      totalRequests += requestStat.num_requests
      totalFailures += requestStat.num_failures
      totalTime += requestStat.avg_response_time
      requestCount++
    })
    
    report.value.total_requests = totalRequests
    report.value.success_rate = ((totalRequests - totalFailures) / Math.max(totalRequests, 1)) * 100
    report.value.avg_response_time = totalTime / Math.max(requestCount, 1)
  }
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
</script>

<style scoped>
.report-detail {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.realtime-stats {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
}

.realtime-stats .stat-item {
  text-align: center;
  padding: 10px;
  min-width: 120px;
}

.realtime-stats .stat-label {
  font-size: 14px;
  color: #666;
}

.realtime-stats .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-top: 5px;
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

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.mt-20 {
  margin-top: 20px;
}

.response-time-stats {
  display: flex;
  justify-content: space-around;
}

.response-time-stats .stat-item {
  text-align: center;
}

.response-time-stats .stat-label {
  font-size: 14px;
  color: #666;
}

.response-time-stats .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-top: 5px;
}
</style>
