<template>
  <div class="favorite-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Star /></el-icon>
        我的收藏
      </h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 标签筛选 -->
    <el-card class="filter-card" v-if="allTags.length > 0">
      <div class="tag-filter">
        <span class="filter-label">标签筛选：</span>
        <el-tag
          v-for="tag in allTags"
          :key="tag.tag"
          :type="selectedTag === tag.tag ? 'primary' : 'info'"
          class="tag-item"
          effect="plain"
          @click="filterByTag(tag.tag)"
          style="cursor: pointer"
        >
          {{ tag.tag }} ({{ tag.count }})
        </el-tag>
        <el-tag v-if="selectedTag" type="danger" effect="plain" @click="filterByTag(null)" style="cursor: pointer">
          清除筛选
        </el-tag>
      </div>
    </el-card>

    <el-table
      :data="favoriteList"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="news_info.title" label="标题" min-width="300">
        <template #default="{ row }">
          <a
            v-if="row.news_info?.source_url"
            :href="row.news_info.source_url"
            target="_blank"
            class="news-title-link"
          >
            {{ row.news_info?.title || '无标题' }}
          </a>
          <span v-else class="news-title">{{ row.news_info?.title || '无标题' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="news_info.category" label="分类" width="100">
        <template #default="{ row }">
          <el-tag :type="getCategoryType(row.news_info?.category)" size="small">
            {{ getCategoryLabel(row.news_info?.category) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="news_info.source_name" label="来源" width="120" />
      <el-table-column label="标签" width="200">
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags_list"
            :key="tag"
            size="small"
            class="tag-item"
            closable
            @close="removeTag(row, tag)"
          >
            {{ tag }}
          </el-tag>
          <el-button type="primary" text size="small" @click="openTagDialog(row)">
            + 标签
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="收藏时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="danger"
            text
            size="small"
            @click="handleDelete(row)"
          >
            取消收藏
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container" v-if="favoriteList.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-empty v-if="!loading && favoriteList.length === 0" description="暂无收藏内容">
      <el-button type="primary" @click="$router.push('/oil-gas')">去浏览新闻</el-button>
    </el-empty>

    <!-- 标签编辑弹窗 -->
    <el-dialog v-model="tagDialogVisible" title="编辑标签" width="400px">
      <div class="tag-editor">
        <div class="preset-tags">
          <span class="label">快捷标签：</span>
          <el-tag
            v-for="preset in presetTags"
            :key="preset"
            :type="editingTags.includes(preset) ? 'primary' : 'info'"
            effect="plain"
            style="cursor: pointer; margin: 4px"
            @click="toggleTag(preset)"
          >
            {{ preset }}
          </el-tag>
        </div>
        <div class="current-tags" style="margin-top: 12px">
          <span class="label">当前标签：</span>
          <el-tag
            v-for="tag in editingTags"
            :key="tag"
            closable
            style="margin: 4px"
            @close="editingTags = editingTags.filter(t => t !== tag)"
          >
            {{ tag }}
          </el-tag>
          <span v-if="editingTags.length === 0" style="color: #999">无标签</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTags">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Star, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { favoriteApi } from '../api/index'

const loading = ref(false)
const favoriteList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const allTags = ref([])
const selectedTag = ref(null)

const presetTags = ['#重要', '#待跟进', '#已处理']
const tagDialogVisible = ref(false)
const editingTags = ref([])
const editingFavorite = ref(null)

const getCategoryType = (category) => {
  const map = { oil_gas: 'warning', wind_power: 'success', ffml: 'primary' }
  return map[category] || 'info'
}

const getCategoryLabel = (category) => {
  const map = { oil_gas: '油气', wind_power: '风电', ffml: 'FFML' }
  return map[category] || '综合'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const loadFavoriteList = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (selectedTag.value) params.tag = selectedTag.value
    const res = await favoriteApi.getList(params)
    favoriteList.value = res.data?.data?.list || []
    total.value = res.data?.data?.total || 0
  } catch (error) {
    ElMessage.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  try {
    const res = await favoriteApi.getTags()
    allTags.value = res.data?.data || []
  } catch (e) {}
}

const filterByTag = (tag) => {
  selectedTag.value = tag
  currentPage.value = 1
  loadFavoriteList()
}

const handleRefresh = () => {
  loadFavoriteList()
  loadTags()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadFavoriteList()
}

const handleCurrentChange = () => {
  loadFavoriteList()
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', { type: 'warning' })
    await favoriteApi.remove(row.id)
    ElMessage.success('已取消收藏')
    loadFavoriteList()
    loadTags()
  } catch (e) {}
}

const openTagDialog = (row) => {
  editingFavorite.value = row
  editingTags.value = [...(row.tags_list || [])]
  tagDialogVisible.value = true
}

const toggleTag = (tag) => {
  if (editingTags.value.includes(tag)) {
    editingTags.value = editingTags.value.filter(t => t !== tag)
  } else {
    editingTags.value.push(tag)
  }
}

const saveTags = async () => {
  try {
    await favoriteApi.updateTags(editingFavorite.value.id, editingTags.value)
    ElMessage.success('标签更新成功')
    tagDialogVisible.value = false
    loadFavoriteList()
    loadTags()
  } catch (e) {
    ElMessage.error('更新标签失败')
  }
}

const removeTag = async (row, tag) => {
  const newTags = (row.tags_list || []).filter(t => t !== tag)
  try {
    await favoriteApi.updateTags(row.id, newTags)
    row.tags_list = newTags
    loadTags()
  } catch (e) {
    ElMessage.error('删除标签失败')
  }
}

onMounted(() => {
  loadFavoriteList()
  loadTags()
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

:deep(.page-header .el-button) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.filter-card {
  margin-bottom: 20px;
}

.tag-filter {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label, .label {
  font-weight: 600;
  color: #606266;
}

.tag-item {
  margin: 2px 4px;
}

.news-title-link {
  color: #409EFF;
  text-decoration: none;
}

.news-title-link:hover {
  text-decoration: underline;
}

.news-title {
  color: #303133;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
}
</style>
