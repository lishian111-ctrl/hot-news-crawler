<template>
  <el-card class="news-card" shadow="hover" @click="handleClick">
    <template #header>
      <div class="card-header">
        <el-tag :type="getCategoryType(news.category)" size="small">
          {{ news.category || '综合' }}
        </el-tag>
        <el-button
          type="info"
          :icon="isFavorited ? Star : Star"
          circle
          size="small"
          @click.stop="toggleFavorite"
          :class="{ 'is-favorited': isFavorited }"
        />
      </div>
    </template>

    <div class="news-content">
      <!-- 标题 -->
      <h3 class="news-title" :title="news.title">
        {{ news.title }}
      </h3>

      <!-- 摘要 -->
      <p class="news-summary" v-if="news.summary">
        {{ news.summary }}
      </p>

      <!-- 图片 -->
      <div class="news-image" v-if="news.image">
        <el-image
          :src="news.image"
          fit="cover"
          class="cover-image"
          :preview-src-list="[news.image]"
        />
      </div>

      <!-- 底部信息 -->
      <div class="news-footer">
        <span class="news-source" :title="news.source_name">
          <el-icon><Document /></el-icon>
          {{ news.source_name || '未知来源' }}
        </span>
        <span class="news-time">
          <el-icon><Clock /></el-icon>
          {{ formatTime(news.publish_time) }}
        </span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Clock, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['favorite', 'click'])

const isFavorited = ref(false)

// 检查是否已收藏
onMounted(() => {
  if (props.news.isFavorite !== undefined) {
    isFavorited.value = props.news.isFavorite
  }
})

// 获取分类标签类型
const getCategoryType = (category) => {
  const typeMap = {
    '油气': 'warning',
    '风电': 'success',
    'FFML': 'primary',
    '热点': 'danger',
    '综合': 'info',
    'oil_gas': 'warning',
    'wind_power': 'success',
    'ffml': 'primary'
  }
  return typeMap[category] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleDateString('zh-CN')
}

// 切换收藏状态
const toggleFavorite = () => {
  isFavorited.value = !isFavorited.value
  emit('favorite', { ...props.news, isFavorite: isFavorited.value })
  ElMessage.success(isFavorited.value ? '已添加到收藏' : '已取消收藏')
}

// 处理点击 - 跳转到详情页
const handleClick = () => {
  router.push(`/news/${props.news.id}`)
}
</script>

<style scoped>
.news-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.news-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.news-summary {
  font-size: 14px;
  color: #606266;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-height: 1.6;
}

.news-image {
  width: 100%;
  height: 160px;
  border-radius: 4px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.news-source,
.news-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-button.is-favorited) {
  color: #e6a23c;
}
</style>
