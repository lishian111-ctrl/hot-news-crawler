<template>
  <div class="source-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Collection /></el-icon>
        信源管理
      </h1>
      <div class="header-actions">
        <el-upload
          :show-file-list="false"
          accept=".xlsx"
          :before-upload="handleImportExcel"
        >
          <el-button>
            <el-icon><Upload /></el-icon>
            导入 Excel
          </el-button>
        </el-upload>
        <el-button @click="handleExportExcel">
          <el-icon><Download /></el-icon>
          导出 Excel
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加信源
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="信源名称">
          <el-input v-model="searchForm.keyword" placeholder="搜索信源名称或URL" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="所属板块">
          <el-select v-model="searchForm.board" placeholder="全部板块" clearable style="width: 140px">
            <el-option label="油气行业" value="油气行业" />
            <el-option label="海上风电" value="海上风电" />
            <el-option label="FFML" value="FFML" />
          </el-select>
        </el-form-item>
        <el-form-item label="信源分类">
          <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width: 140px">
            <el-option label="政府官网" value="政府官网" />
            <el-option label="行业协会" value="行业协会" />
            <el-option label="央企国企" value="央企国企" />
            <el-option label="行业媒体" value="行业媒体" />
            <el-option label="国际机构" value="国际机构" />
            <el-option label="一般网站" value="一般网站" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 信源列表 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="sourceList" style="width: 100%">
        <el-table-column prop="name" label="信源名称" min-width="160" />
        <el-table-column prop="url" label="地址" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <a :href="row.url" target="_blank" class="source-link">{{ row.url }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="board" label="板块" width="110">
          <template #default="{ row }">
            <el-tag :type="getBoardTag(row.board)" size="small">{{ getBoardLabel(row.board) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="110">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.category || '未分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.weight >= 8 ? 'danger' : row.weight >= 5 ? 'warning' : 'info'" size="small">
              {{ row.weight }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入信源名称" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="formData.url" placeholder="请输入采集 URL" />
        </el-form-item>
        <el-form-item label="板块" prop="board">
          <el-select v-model="formData.board" placeholder="请选择板块" style="width: 100%">
            <el-option label="油气行业" value="油气行业" />
            <el-option label="海上风电" value="海上风电" />
            <el-option label="FFML" value="FFML" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="政府官网" value="政府官网" />
            <el-option label="行业协会" value="行业协会" />
            <el-option label="央企国企" value="央企国企" />
            <el-option label="行业媒体" value="行业媒体" />
            <el-option label="国际机构" value="国际机构" />
            <el-option label="一般网站" value="一般网站" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-slider v-model="formData.weight" :min="1" :max="10" show-stops />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Collection, Plus, Upload, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sourceApi } from '../api/index'

const loading = ref(false)
const submitting = ref(false)
const sourceList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editMode = ref(false)

const searchForm = reactive({ keyword: '', board: '', category: '' })

const formData = reactive({
  id: null,
  name: '',
  url: '',
  board: '',
  category: '',
  weight: 5
})

const formRules = {
  name: [{ required: true, message: '请输入信源名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入 URL', trigger: 'blur' }],
  board: [{ required: true, message: '请选择板块', trigger: 'change' }]
}

const formRef = ref(null)
const dialogTitle = computed(() => editMode.value ? '编辑信源' : '添加信源')

const getBoardLabel = (board) => {
  return board || '未分类'
}

const getBoardTag = (board) => {
  const map = { '油气行业': 'warning', '海上风电': 'success', 'FFML': 'primary' }
  return map[board] || 'info'
}

const loadSourceList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    // 去掉空值
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const res = await sourceApi.getList(params)
    sourceList.value = res.data?.data?.list || []
    total.value = res.data?.data?.total || 0
  } catch (e) {
    ElMessage.error('加载信源列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; loadSourceList() }
const handleReset = () => {
  Object.assign(searchForm, { keyword: '', board: '', category: '' })
  handleSearch()
}
const handleSizeChange = () => { currentPage.value = 1; loadSourceList() }
const handleCurrentChange = () => { loadSourceList() }

const handleAdd = () => {
  editMode.value = false
  Object.assign(formData, { id: null, name: '', url: '', board: '', category: '', weight: 5 })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editMode.value = true
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    url: row.url,
    board: row.board,
    category: row.category,
    weight: row.weight || 5
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除信源「${row.name}」？`, '提示', { type: 'warning' })
    await sourceApi.delete(row.id)
    ElMessage.success('删除成功')
    loadSourceList()
  } catch (e) {}
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    if (editMode.value) {
      await sourceApi.update(formData.id, {
        name: formData.name,
        url: formData.url,
        board: formData.board,
        category: formData.category,
        weight: formData.weight
      })
      ElMessage.success('更新成功')
    } else {
      await sourceApi.add({
        name: formData.name,
        url: formData.url,
        board: formData.board,
        category: formData.category,
        weight: formData.weight
      })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadSourceList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleImportExcel = async (file) => {
  try {
    const res = await sourceApi.importExcel(file)
    const data = res.data?.data || {}
    ElMessage.success(`导入成功：${data.imported_count} 条，失败：${data.error_count} 条`)
    loadSourceList()
  } catch (e) {
    ElMessage.error('导入失败')
  }
  return false // 阻止 el-upload 默认上传
}

const handleExportExcel = async () => {
  try {
    const res = await sourceApi.exportExcel()
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `信源列表_${new Date().toISOString().slice(0, 10)}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => { loadSourceList() })
</script>

<style scoped>
.source-page { padding: 20px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  color: #fff;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.page-header :deep(.el-button) {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.3);
  color: #fff;
}

.search-card { margin-bottom: 20px; }
.table-card { margin-bottom: 20px; }
.pagination-container { display: flex; justify-content: center; margin-top: 20px; }

.source-link {
  color: #409EFF;
  text-decoration: none;
}
.source-link:hover {
  text-decoration: underline;
}
</style>
