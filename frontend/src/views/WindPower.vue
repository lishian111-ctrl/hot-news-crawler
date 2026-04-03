<template>
  <div class="wind-power-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Odometer /></el-icon>
        海上风电行业
      </h1>
      <el-button type="success" @click="handleRefresh" :loading="loading">
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
import { Odometer, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import TimelineNewsList from '../components/TimelineNewsList.vue'
import { newsApi, favoriteApi } from '../api/index'

const loading = ref(false)
const newsList = ref([])
const total = ref(0)

const loadNewsList = async (page = 1, pageSize = 20) => {
  loading.value = true
  try {
    const res = await newsApi.getList({ category: 'wind_power', page, page_size: pageSize })
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
    if (news.is_favorite) {
      await favoriteApi.removeByNews(news.id)
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.add({ news_id: news.id, tags: [] })
      ElMessage.success('已添加到收藏')
    }
    loadNewsList()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadNewsList()
})
</script>

<style scoped>
.wind-power-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
