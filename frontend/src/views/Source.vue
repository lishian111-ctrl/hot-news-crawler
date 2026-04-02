<template>
  <div class="source-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Collection /></el-icon>
        信源管理
      </h1>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加信源
      </el-button>
    </div>

    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="信源名称">
          <el-input v-model="searchForm.name" placeholder="请输入信源名称" clearable />
        </el-form-item>
        <el-form-item label="信源类型">
          <el-select v-model="searchForm.type" placeholder="请选择类型" clearable style="width: 150px">
            <el-option label="新闻网站" value="website" />
            <el-option label="RSS 订阅" value="rss" />
            <el-option label="API 接口" value="api" />
            <el-option label="社交媒体" value="social" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" v-loading="loading">
      <el-table :data="sourceList" style="width: 100%">
        <el-table-column prop="name" label="信源名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="地址" min-width="250" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="sourceList.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Collection, Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import sourceApi from '../api/source'

const loading = ref(false)
const sourceList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editMode = ref(false)

const searchForm = reactive({ name: '', type: '', status: '' })

const formData = reactive({
  id: null, name: '', type: '', url: '', category: 'general', status: 'active'
})

const formRules = {
  name: [{ required: true, message: '请输入信源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  url: [{ required: true, message: '请输入 URL', trigger: 'blur' }]
}

const formRef = ref(null)
const dialogTitle = computed(() => editMode.value ? '编辑信源' : '添加信源')

const getTypeLabel = (type) => {
  const map = { website: '新闻网站', rss: 'RSS', api: 'API', social: '社交媒体' }
  return map[type] || type
}

const getTypeTag = (type) => {
  const map = { website: 'primary', rss: 'success', api: 'warning', social: 'danger' }
  return map[type] || 'info'
}

const getCategoryTag = (category) => {
  const map = { oil_gas: 'warning', wind_power: 'success', ffml: 'primary', general: 'info' }
  return map[category] || 'info'
}

const loadSourceList = async (page = 1, size = 20) => {
  loading.value = true
  try {
    const res = await sourceApi.getSourceList({ ...searchForm, page, pageSize: size })
    sourceList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; loadSourceList(1, pageSize.value) }
const handleReset = () => { Object.assign(searchForm, { name: '', type: '', status: '' }); handleSearch() }
const handleSizeChange = (size) => { currentPage.value = 1; loadSourceList(1, size) }
const handleCurrentChange = (page) => { loadSourceList(page, pageSize.value) }

const handleAdd = () => {
  editMode.value = false
  Object.assign(formData, { id: null, name: '', type: '', url: '', category: 'general', status: 'active' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editMode.value = true
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await sourceApi.deleteSource(row.id)
    ElMessage.success('删除成功')
    loadSourceList()
  } catch (e) {}
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    if (editMode.value) {
      await sourceApi.updateSource(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await sourceApi.addSource(formData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadSourceList()
  } catch (e) {}
}

onMounted(() => { loadSourceList() })
</script>

<style scoped>
.source-page { padding: 20px; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px; padding: 16px 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px; color: #fff;
}
.page-title { display: flex; align-items: center; gap: 12px; margin: 0; font-size: 24px; }
.page-header :deep(.el-button) { background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.3); color: #fff; }
.search-card { margin-bottom: 20px; }
.table-card { margin-bottom: 20px; }
.pagination-container { display: flex; justify-content: center; margin-top: 20px; }
</style>
