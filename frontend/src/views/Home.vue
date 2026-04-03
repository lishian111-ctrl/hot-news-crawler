<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <h1>能源行业信息情报系统</h1>
      <p>每日自动采集油气、海上风电、FFML 三大板块行业动态</p>
      <el-button
        class="crawl-btn"
        :loading="crawling"
        :disabled="crawling"
        @click="handleCrawl"
      >
        {{ crawling ? '采集中，请稍候...' : '立即采集最新资讯' }}
      </el-button>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card oil-gas-card" @click="$router.push('/oil-gas')">
          <div class="stat-icon"><el-icon :size="32"><Histogram /></el-icon></div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.oilGas }}</div>
            <div class="stat-label">油气行业</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card wind-card" @click="$router.push('/wind-power')">
          <div class="stat-icon"><el-icon :size="32"><Odometer /></el-icon></div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.windPower }}</div>
            <div class="stat-label">海上风电</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card ffml-card" @click="$router.push('/ffml')">
          <div class="stat-icon"><el-icon :size="32"><DataAnalysis /></el-icon></div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.ffml }}</div>
            <div class="stat-label">FFML</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card hot-card" @click="$router.push('/hot')">
          <div class="stat-icon"><el-icon :size="32"><Promotion /></el-icon></div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">全部资讯</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新热点 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="latest-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新资讯</span>
              <el-button type="primary" text @click="$router.push('/hot')">查看更多</el-button>
            </div>
          </template>
          <div v-loading="loading">
            <div v-for="item in latestNews" :key="item.id" class="news-item" @click="openNews(item)">
              <div class="news-item-left">
                <el-tag :type="getCategoryType(item.category)" size="small">
                  {{ getCategoryLabel(item.category) }}
                </el-tag>
                <span class="news-item-title">{{ item.title }}</span>
              </div>
              <span class="news-item-time">{{ formatTime(item.publish_time) }}</span>
            </div>
            <el-empty v-if="latestNews.length === 0" description="暂无数据，等待首次采集" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <HotRanking
          title="今日热点 TOP10"
          :ranking-list="hotRanking"
          :loading="rankingLoading"
          @refresh="loadHotRanking"
          @click="openNews"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Histogram, Odometer, DataAnalysis, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import HotRanking from '../components/HotRanking.vue'
import { newsApi, hotApi, crawlApi } from '../api/index'

const router = useRouter()

const loading = ref(false)
const rankingLoading = ref(false)
const crawling = ref(false)
const latestNews = ref([])
const hotRanking = ref([])
const stats = ref({ oilGas: 0, windPower: 0, ffml: 0, total: 0 })

const getCategoryType = (cat) => {
  const m = { oil_gas: 'warning', wind_power: 'success', ffml: 'primary' }
  return m[cat] || 'info'
}

const getCategoryLabel = (cat) => {
  const m = { oil_gas: '油气', wind_power: '风电', ffml: 'FFML' }
  return m[cat] || '综合'
}

const formatTime = (time) => {
  if (!time) return ''
  const d = new Date(time)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.max(1, Math.floor(diff / 60000))}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

const openNews = (news) => {
  router.push(`/news/${news.id}`)
}

const loadLatestNews = async () => {
  loading.value = true
  try {
    const res = await newsApi.getList({ page: 1, page_size: 15 })
    latestNews.value = res.data?.data?.list || []
  } catch (e) {} finally {
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
  } catch (e) {} finally {
    rankingLoading.value = false
  }
}

const loadStats = async () => {
  try {
    const cats = ['oil_gas', 'wind_power', 'ffml']
    const results = await Promise.all(cats.map(c => newsApi.getList({ category: c, page: 1, page_size: 1 })))
    stats.value.oilGas = results[0].data?.data?.total || 0
    stats.value.windPower = results[1].data?.data?.total || 0
    stats.value.ffml = results[2].data?.data?.total || 0
    stats.value.total = stats.value.oilGas + stats.value.windPower + stats.value.ffml
  } catch (e) {}
}

const handleCrawl = async () => {
  crawling.value = true
  try {
    await crawlApi.run()
    ElMessage.success('采集任务已启动，正在后台运行，约需 1~3 分钟，完成后刷新页面即可看到新闻')
    // 30秒后自动刷新数据
    setTimeout(() => {
      loadLatestNews()
      loadHotRanking()
      loadStats()
      crawling.value = false
    }, 30000)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '启动采集失败')
    crawling.value = false
  }
}

onMounted(() => {
  loadLatestNews()
  loadHotRanking()
  loadStats()
})
</script>

<style scoped>
.home-page {
  padding: 20px;
}

.welcome-banner {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
  margin-bottom: 24px;
}

.welcome-banner h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
}

.welcome-banner p {
  margin: 0 0 20px 0;
  opacity: 0.85;
  font-size: 16px;
}

.crawl-btn {
  background: rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.6);
  color: #fff;
  font-size: 15px;
  padding: 10px 28px;
  border-radius: 24px;
}

.crawl-btn:hover {
  background: rgba(255,255,255,0.4);
}

.stat-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  margin-right: 16px;
  padding: 12px;
  border-radius: 12px;
  color: #fff;
}

.oil-gas-card .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.wind-card .stat-icon { background: linear-gradient(135deg, #11998e, #38ef7d); }
.ffml-card .stat-icon { background: linear-gradient(135deg, #56ab2f, #a8e063); }
.hot-card .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.latest-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.news-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.news-item:hover {
  background: #f5f7fa;
  margin: 0 -20px;
  padding: 12px 20px;
}

.news-item:last-child {
  border-bottom: none;
}

.news-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.news-item-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
  font-size: 14px;
}

.news-item-time {
  color: #909399;
  font-size: 12px;
  flex-shrink: 0;
  margin-left: 16px;
}
</style>
