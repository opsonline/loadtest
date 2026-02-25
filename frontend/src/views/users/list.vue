<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>添加用户
      </el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="searchForm.search" 
            placeholder="用户名或邮箱" 
            @keyup.enter="fetchUsers"
            clearable
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="选择角色" @change="fetchUsers" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="只读用户" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editUser(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 编辑/创建用户对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingUser ? '编辑用户' : '创建用户'" width="500px">
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%;">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="只读用户" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" autocomplete="off" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { userApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const users = ref([])
const showCreateDialog = ref(false)
const editingUser = ref(null)
const pagination = ref({
  current: 1,
  size: 10,
  total: 0
})

const searchForm = ref({
  search: '',
  role: ''
})

const userForm = ref({
  username: '',
  email: '',
  role: 'user',
  password: ''
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: !editingUser.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const userFormRef = ref(null)

onMounted(() => {
  fetchUsers()
})

const fetchUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.value.current,
      page_size: pagination.value.size,
      ...searchForm.value
    }
    const data = await userApi.list(params)
    users.value = data.results || data.users || []
    pagination.value.total = data.count || users.value.length
  } catch (error) {
    console.error('Failed to fetch users:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const getRoleText = (role) => {
  const map = {
    'admin': '管理员',
    'user': '普通用户',
    'viewer': '只读用户'
  }
  return map[role] || role
}

const getRoleTagType = (role) => {
  const map = {
    'admin': 'danger',
    'user': 'primary',
    'viewer': 'info'
  }
  return map[role] || 'primary'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const editUser = (row) => {
  editingUser.value = row
  userForm.value = {
    username: row.username,
    email: row.email,
    role: row.role
  }
  showCreateDialog.value = true
}

const saveUser = async () => {
  try {
    await userFormRef.value.validate()
    
    saving.value = true
    if (editingUser.value) {
      // 更新用户角色
      await userApi.updateUserRole(editingUser.value.id, { role: userForm.value.role })
      ElMessage.success('用户更新成功')
    } else {
      // 创建用户
      await userApi.register(userForm.value)
      ElMessage.success('用户创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    fetchUsers()
  } catch (error) {
    console.error('Save user error:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', { 
      type: 'warning' 
    })
    
    await userApi.delete(row.id)
    ElMessage.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete user error:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const resetForm = () => {
  userForm.value = {
    username: '',
    email: '',
    role: 'user',
    password: ''
  }
  editingUser.value = null
}

const handleSizeChange = (size) => {
  pagination.value.size = size
  fetchUsers()
}

const handleCurrentChange = (page) => {
  pagination.value.current = page
  fetchUsers()
}
</script>

<style scoped>
.users-page {
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

.search-form {
  margin-bottom: 20px;
}
</style>