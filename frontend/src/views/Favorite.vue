<template>
  <div class="favorite-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Star /></el-icon>
        我的收藏
      </h1>
      <div class="header-actions">
        <el-button 
          type="danger" 
          plain 
          @click="handleBatchDelete"
          :disabled="selectedIds.length === 0"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button type="primary" @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-table
      v-model:selection-rows="selectedRows"
      :data="favoriteList"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="title" label="标题" min-width="300">
        <template #default="{ row }">
          <span class="news-title" :title="row.title">{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="100">
        <template #default="{ row }">
          <el-tag :type="getCategoryType(row.category)" size="small">
            {{ row.category || '综合' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column prop="publishTime" label="发布时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.publishTime) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            type="danger"
            text
            size="small"
            @click="handleDelete(row)"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container" v-if="favoriteList.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && favoriteList.length === 0" description="暂无收藏内容">
      <el-button type="primary" @click="$router.push('/')">去浏览新闻</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Star, Refresh, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import newsApi from '../api/news'

const loading = ref(false)
const favoriteList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedRows = ref([])
const selectedIds = ref([])

// 获取分类标签类型
const getCategoryType = (category) => {
  const typeMap = {
    '油气': 'warning',
    '风电': 'success',
    'FFML': 'primary',
    '热点': 'danger',
    '综合': 'info'
  }
  return typeMap[category] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

// 加载收藏列表
const loadFavoriteList = async (page = 1, pageSize = 20) => {
  loading.value = true
  try {
    const res = await newsApi.getFavoriteList({ page, pageSize })
    favoriteList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载收藏列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 处理刷新
const handleRefresh = () => {
  loadFavoriteList(currentPage.value, pageSize.value)
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  currentPage.value = 1
  loadFavoriteList(1, size)
}

// 处理页码变化
const handleCurrentChange = (page) => {
  loadFavoriteList(page, pageSize.value)
}

// 处理删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await newsApi.removeFavorite(row.id)
    ElMessage.success('已取消收藏')
    loadFavoriteList(currentPage.value, pageSize.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 项收藏吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await newsApi.batchRemoveFavorite(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    selectedRows.value = []
    loadFavoriteList(currentPage.value, pageSize.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

onMounted(() => {
  loadFavoriteList()
})
</script>

<style scoped>
.favorite-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  border-radius: 12px;
  color: #fff;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

:deep(.el-button:hover:not(.el-button--plain)) {
  background: rgba(255, 255, 255, 0.3);
}

:deep(.el-button--plain) {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

:deep(.el-button--plain:hover) {
  background: rgba(255, 255, 255, 0.2);
  border-color: #fff;
  color: #fff;
}

.news-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 20px 0;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
}
</style>
