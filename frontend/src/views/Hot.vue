<template>
  <div class="hot-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Promotion /></el-icon>
        每日热点
      </h1>
      <div class="header-actions">
        <el-radio-group v-model="timeRange" size="small" @change="handleRefresh">
          <el-radio-button label="today">今日</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
        </el-radio-group>
        <el-button type="danger" @click="handleRefresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 热点排行 -->
      <el-col :xs="24" :lg="8">
        <HotRanking
          title="全网热点 TOP10"
          :ranking-list="hotRanking"
          :loading="rankingLoading"
          @refresh="handleRefresh"
          @click="handleNewsClick"
        />
      </el-col>

      <!-- 新闻列表 -->
      <el-col :xs="24" :lg="16">
        <div class="hot-news-section">
          <h2 class="section-title">
            <el-icon><Document /></el-icon>
            热点资讯
          </h2>
          <NewsList
            :news-list="newsList"
            :total="total"
            @load="handleLoad"
            @favorite="handleFavorite"
          />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Promotion, Refresh, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NewsList from '../components/NewsList.vue'
import HotRanking from '../components/HotRanking.vue'
import { hotApi, favoriteApi } from '../api/index'

const router = useRouter()

const loading = ref(false)
const rankingLoading = ref(false)
const timeRange = ref('today')
const newsList = ref([])
const total = ref(0)
const hotRanking = ref([])

const loadNewsList = async (page = 1, pageSize = 20) => {
  loading.value = true
  try {
    const res = await hotApi.getDaily({ limit: 30 })
    const list = res.data?.data?.list || []
    newsList.value = list
    total.value = list.length
  } catch (error) {
    ElMessage.error('加载热点新闻失败')
  } finally {
    loading.value = false
  }
}

const loadHotRanking = async () => {
  rankingLoading.value = true
  try {
    const res = await hotApi.getDaily({ limit: 10 })
    hotRanking.value = (res.data?.data?.list || []).map(item => ({
      ...item,
      hotValue: item.score
    }))
  } catch (error) {
    console.error(error)
  } finally {
    rankingLoading.value = false
  }
}

const handleRefresh = () => {
  loadNewsList()
  loadHotRanking()
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

const handleNewsClick = (news) => {
  router.push(`/news/${news.id}`)
}

onMounted(() => {
  loadNewsList()
  loadHotRanking()
})
</script>

<style scoped>
.hot-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

:deep(.el-radio-group .el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

:deep(.el-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #fff;
  border-color: #fff;
  color: #f56c6c;
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

:deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.3);
}

.hot-news-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}
</style>
