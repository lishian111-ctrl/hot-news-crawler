<template>
  <div class="timeline-news-container" v-loading="loading">
    <div class="timeline-wrapper">
      <!-- 左侧时间轴线 -->
      <div class="timeline-axis">
        <div class="axis-line"></div>
      </div>

      <!-- 右侧新闻列表 -->
      <div class="timeline-news-list">
        <div
          v-for="(news, index) in newsList"
          :key="news.id"
          class="timeline-news-item"
          :style="{ animationDelay: `${index * 0.1}s` }"
          @click="handleNewsClick(news)"
        >
          <!-- 时间轴节点 - 与新闻标题对齐 -->
          <div class="timeline-dot">
            <div class="dot-inner"></div>
          </div>

          <!-- 新闻卡片 -->
          <div class="timeline-news-card">
            <!-- 时间标签 -->
            <div class="news-time-label">
              <el-icon><Clock /></el-icon>
              <span>{{ formatNewsTime(news.publish_time) }}</span>
            </div>

            <!-- 新闻内容 -->
            <div class="news-body">
              <div class="news-main">
                <h3 class="news-title" :title="news.title">
                  {{ news.title }}
                </h3>
                <p class="news-summary" v-if="news.summary || news.content">
                  {{ getSummary(news) }}
                </p>
              </div>

              <!-- 新闻脚注 -->
              <div class="news-footer">
                <div class="news-meta">
                  <el-tag :type="getCategoryType(news.category)" size="small">
                    {{ getCategoryLabel(news.category) }}
                  </el-tag>
                  <span class="news-source" :title="news.source_name">
                    <el-icon><Document /></el-icon>
                    {{ news.source_name || '未知来源' }}
                  </span>
                </div>
                <div class="news-actions">
                  <el-button
                    :type="news.is_favorite ? 'warning' : 'info'"
                    :icon="Star"
                    circle
                    size="small"
                    @click.stop="toggleFavorite(news)"
                  />
                  <el-button
                    type="primary"
                    size="small"
                    text
                    @click.stop="openDetail(news.id)"
                  >
                    查看详情
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-if="newsList.length === 0" description="暂无新闻数据" />
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="pagination && newsList.length > 0">
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
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, Document, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  newsList: {
    type: Array,
    default: () => []
  },
  pagination: {
    type: Boolean,
    default: true
  },
  total: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['load', 'favorite'])

const router = useRouter()
const currentPage = ref(1)
const pageSize = ref(20)

// 格式化时间
const formatNewsTime = (time) => {
  if (!time) return '时间未知'
  const date = new Date(time)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleString('zh-CN')
}

// 获取摘要
const getSummary = (news) => {
  if (news.summary) {
    return news.summary.length > 100 ? news.summary.slice(0, 100) + '...' : news.summary
  }
  if (news.content) {
    const text = news.content.replace(/<[^>]*>/g, '')
    return text.length > 100 ? text.slice(0, 100) + '...' : text
  }
  return ''
}

// 获取分类类型
const getCategoryType = (category) => {
  const typeMap = {
    'oil_gas': 'warning',
    'wind_power': 'success',
    'ffml': 'primary',
    '油气': 'warning',
    '风电': 'success',
    'FFML': 'primary',
    '热点': 'danger',
    '综合': 'info'
  }
  return typeMap[category] || 'info'
}

// 获取分类标签
const getCategoryLabel = (category) => {
  const labelMap = {
    'oil_gas': '油气',
    'wind_power': '风电',
    'ffml': 'FFML',
    '油气': '油气',
    '风电': '风电',
    'FFML': 'FFML',
    '热点': '热点',
    '综合': '综合'
  }
  return labelMap[category] || category || '综合'
}

// 打开详情页
const openDetail = (newsId) => {
  console.log('openDetail 被调用，newsId:', newsId)
  const path = `/news/${newsId}`
  console.log('准备路由到:', path)
  router.push(path)
}

// 点击新闻
const handleNewsClick = (news) => {
  console.log('handleNewsClick 被调用，news:', news)
  console.log('点击新闻，ID:', news.id)
  const path = `/news/${news.id}`
  console.log('准备路由到:', path)
  router.push(path)
}

// 切换收藏
const toggleFavorite = async (news) => {
  emit('favorite', { ...news, is_favorite: !news.is_favorite })
}

// 分页处理
const handleSizeChange = (size) => {
  currentPage.value = 1
  emit('load', { page: 1, pageSize: size })
}

const handleCurrentChange = (page) => {
  emit('load', { page, pageSize: pageSize.value })
}

// 监听分页变化
watch([currentPage, pageSize], ([newPage, newSize]) => {
  emit('load', { page: newPage, pageSize: newSize })
})
</script>

<style scoped>
.timeline-news-container {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  min-height: 500px;
}

.timeline-wrapper {
  display: flex;
  position: relative;
}

/* 时间轴线 */
.timeline-axis {
  width: 40px;
  flex-shrink: 0;
  position: relative;
  padding: 20px 0;
}

.axis-line {
  position: absolute;
  left: 27px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

/* 新闻列表 */
.timeline-news-list {
  flex: 1;
  padding: 20px 0;
}

.timeline-news-item {
  display: flex;
  margin-bottom: 30px;
  opacity: 0;
  animation: slideIn 0.5s ease forwards;
  cursor: pointer;
  position: relative;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.timeline-news-item:hover .timeline-news-card {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  transform: translateX(4px);
}

.timeline-news-item:last-child {
  margin-bottom: 0;
}

/* 时间轴节点 - 与新闻标题对齐 */
.timeline-news-item .timeline-dot {
  position: absolute;
  left: 20px;
  top: 24px;
  width: 14px;
  height: 14px;
  background: #fff;
  border: 3px solid #667eea;
  border-radius: 50%;
  z-index: 2;
  flex-shrink: 0;
}

.timeline-news-item .timeline-dot .dot-inner {
  width: 5px;
  height: 5px;
  background: #667eea;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.timeline-news-card {
  flex: 1;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  transition: all 0.3s ease;
  margin-left: 40px;
}

/* 时间标签 */
.news-time-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #667eea;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 新闻主体 */
.news-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-main {
  flex: 1;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-summary {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 新闻脚注 */
.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.news-source {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.news-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid #f0f0f0;
}

/* 响应式 */
@media (max-width: 768px) {
  .timeline-axis {
    width: 40px;
  }

  .timeline-news-card {
    margin-left: 12px;
    padding: 12px 16px;
  }

  .news-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
