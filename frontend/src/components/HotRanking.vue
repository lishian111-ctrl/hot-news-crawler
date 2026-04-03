<template>
  <div class="hot-ranking-container">
    <el-card class="ranking-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><TrendCharts /></el-icon>
            {{ title }}
          </span>
          <el-button
            type="primary"
            text
            size="small"
            @click="handleRefresh"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-skeleton :rows="10" animated v-if="loading" />

      <div v-else class="ranking-list">
        <div
          v-for="(item, index) in rankingList"
          :key="item.id || index"
          class="ranking-item"
          @click="handleClick(item)"
        >
          <div class="ranking-index" :class="getRankClass(index)">
            {{ index + 1 }}
          </div>
          <div class="ranking-info">
            <div class="ranking-title" :title="item.title">
              {{ item.title }}
            </div>
            <div class="ranking-meta">
              <span class="ranking-hot" v-if="item.hotValue !== undefined">
                <el-icon><Promotion /></el-icon>
                {{ formatHotValue(item.hotValue) }}
              </span>
              <span class="ranking-time" v-if="item.publishTime">
                <el-icon><Clock /></el-icon>
                {{ formatTime(item.publishTime) }}
              </span>
            </div>
          </div>
        </div>

        <el-empty v-if="rankingList.length === 0" description="暂无排行数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { TrendCharts, Refresh, Promotion, Clock } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '热点排行'
  },
  rankingList: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'click'])

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'rank-first'
  if (index === 1) return 'rank-second'
  if (index === 2) return 'rank-third'
  return ''
}

// 格式化热度值
const formatHotValue = (value) => {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(1)}亿`
  }
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }
  return value.toString()
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

  return date.toLocaleDateString('zh-CN')
}

// 处理刷新
const handleRefresh = () => {
  emit('refresh')
}

// 处理点击
const handleClick = (item) => {
  emit('click', item)
}
</script>

<style scoped>
.hot-ranking-container {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.ranking-item:hover {
  background-color: #f5f7fa;
}

.ranking-index {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  background-color: #f5f7fa;
  flex-shrink: 0;
}

.ranking-index.rank-first {
  color: #fff;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.ranking-index.rank-second {
  color: #fff;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.ranking-index.rank-third {
  color: #fff;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.ranking-info {
  flex: 1;
  min-width: 0;
}

.ranking-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.ranking-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.ranking-hot,
.ranking-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ranking-hot {
  color: #f56c6c;
}
</style>
