<template>
  <div class="oil-gas-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><GasStation /></el-icon>
        油气行业资讯
      </h1>
      <el-button type="primary" @click="handleRefresh" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="20">
      <!-- 左侧新闻列表 -->
      <el-col :xs="24" :lg="16">
        <NewsList
          :news-list="newsList"
          :total="total"
          @load="handleLoad"
          @favorite="handleFavorite"
        />
      </el-col>

      <!-- 右侧热点排行 -->
      <el-col :xs="24" :lg="8">
        <HotRanking
          title="油气热点排行"
          :ranking-list="hotRanking"
          :loading="rankingLoading"
          @refresh="handleRefresh"
          @click="handleNewsClick"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { GasStation, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NewsList from '../components/NewsList.vue'
import HotRanking from '../components/HotRanking.vue'
import newsApi from '../api/news'

const loading = ref(false)
const rankingLoading = ref(false)
const newsList = ref([])
const total = ref(0)
const hotRanking = ref([])

// 加载新闻列表
const loadNewsList = async (page = 1, pageSize = 20) => {
  loading.value = true
  try {
    const res = await newsApi.getNewsList({
      category: 'oil_gas',
      page,
      pageSize
    })
    newsList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载新闻列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 加载热点排行
const loadHotRanking = async () => {
  rankingLoading.value = true
  try {
    const res = await newsApi.getHotRanking({ category: 'oil_gas' })
    hotRanking.value = res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    rankingLoading.value = false
  }
}

// 处理刷新
const handleRefresh = () => {
  loadNewsList()
  loadHotRanking()
}

// 处理加载
const handleLoad = ({ page, pageSize }) => {
  loadNewsList(page, pageSize)
}

// 处理收藏
const handleFavorite = async (news) => {
  try {
    await newsApi.toggleFavorite(news.id)
    ElMessage.success(news.isFavorite ? '已添加到收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 处理新闻点击
const handleNewsClick = (news) => {
  ElMessage.info(`点击：${news.title}`)
}

onMounted(() => {
  loadNewsList()
  loadHotRanking()
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
