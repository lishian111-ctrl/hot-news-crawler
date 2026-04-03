<template>
  <div class="oil-gas-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Histogram /></el-icon>
        油气行业资讯
      </h1>
      <el-button type="primary" @click="handleRefresh" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 时间线新闻列表 -->
    <TimelineNewsList
      :news-list="newsList"
      :total="total"
      :loading="loading"
      @load="handleLoad"
      @favorite="handleFavorite"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Histogram, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import TimelineNewsList from '../components/TimelineNewsList.vue'
import { newsApi, favoriteApi } from '../api/index'

const loading = ref(false)
const newsList = ref([])
const total = ref(0)

const loadNewsList = async (page = 1, pageSize = 20) => {
  loading.value = true
  try {
    const res = await newsApi.getList({ category: 'oil_gas', page, page_size: pageSize })
    newsList.value = res.data?.data?.list || []
    total.value = res.data?.data?.total || 0
  } catch (error) {
    ElMessage.error('加载新闻列表失败')
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadNewsList()
}

const handleLoad = ({ page, pageSize }) => {
  loadNewsList(page, pageSize)
}

const handleFavorite = async (news) => {
  try {
    console.log('准备收藏操作，news:', news)
    if (news.is_favorite) {
      console.log('取消收藏，newsId:', news.id)
      await favoriteApi.removeByNews(news.id)
      ElMessage.success('已取消收藏')
    } else {
      console.log('添加收藏，newsId:', news.id)
      const payload = { news_id: news.id, tags: [] }
      console.log('请求 payload:', payload)
      const res = await favoriteApi.add(payload)
      console.log('收藏响应:', res)
      ElMessage.success('已添加到收藏')
    }
    loadNewsList()
  } catch (error) {
    console.error('收藏操作失败，详细错误:', error)
    console.error('错误响应:', error?.response)
    console.error('错误数据:', error?.response?.data)
    ElMessage.error(`操作失败：${error?.response?.data?.detail || error.message}`)
  }
}

onMounted(() => {
  loadNewsList()
})
</script>

<style scoped>
.oil-gas-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

:deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.3);
}
</style>
