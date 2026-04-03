<template>
  <div class="news-detail-page" v-loading="loading">
    <div v-if="news" class="detail-container">
      <!-- 返回按钮和操作栏 -->
      <div class="action-bar">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <div class="action-buttons">
          <el-button @click="openOriginal">
            <el-icon><Link /></el-icon>
            打开原始链接
          </el-button>
          <el-button
            :type="isFavorited ? 'warning' : 'primary'"
            @click="toggleFavorite"
          >
            <el-icon><Star /></el-icon>
            {{ isFavorited ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>

      <!-- 新闻头部 -->
      <div class="news-header">
        <h1 class="news-title">{{ news.title }}</h1>
        <div class="news-meta">
          <el-tag :type="getCategoryType(news.category)" size="default">
            {{ getCategoryLabel(news.category) }}
          </el-tag>
          <span class="meta-item">
            <el-icon><Document /></el-icon>
            {{ news.source_name || '未知来源' }}
          </span>
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatTime(news.publish_time) }}
          </span>
          <span class="meta-item" v-if="news.score">
            <el-icon><TrendCharts /></el-icon>
            热度：{{ news.score }}
          </span>
        </div>
      </div>

      <!-- AI 总结 -->
      <div v-if="news.ai_summary" class="ai-summary-card">
        <div class="ai-summary-header">
          <el-icon class="ai-icon"><MagicStick /></el-icon>
          <span class="ai-title">AI 智能摘要</span>
        </div>
        <div class="ai-summary-content">
          {{ news.ai_summary }}
        </div>
      </div>

      <!-- 翻译提示 -->
      <div v-if="isEnglishContent" class="translation-notice">
        <el-alert
          title="检测到英文内容，已自动翻译为中文"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <!-- 新闻内容 -->
      <div class="news-content" v-if="news.content">
        <div class="content-section">
          <h3 class="section-label">原文内容</h3>
          <div class="original-content" v-html="formattedContent"></div>
        </div>

        <!-- 翻译后的内容 -->
        <div v-if="translatedContent" class="content-section">
          <h3 class="section-label">
            <el-icon><Translate /></el-icon>
            中文翻译
          </h3>
          <div class="translated-content">{{ translatedContent }}</div>
        </div>
      </div>

      <!-- 只有摘要的情况 -->
      <div v-else-if="news.summary" class="summary-only">
        <h3 class="section-label">摘要</h3>
        <p class="summary-text">{{ news.summary }}</p>
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="error-state">
        <el-result icon="error" title="加载失败" :sub-title="error">
          <template #extra>
            <el-button type="primary" @click="loadNewsDetail">重新加载</el-button>
            <el-button @click="goBack">返回列表</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowLeft,
  Link,
  Star,
  Document,
  Clock,
  TrendCharts,
  MagicStick,
  Translate
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { newsApi, favoriteApi, translateApi } from '../api/index'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const news = ref(null)
const error = ref(null)
const isFavorited = ref(false)
const isEnglishContent = ref(false)
const translatedContent = ref('')
const aiSummary = ref('')
const generatingSummary = ref(false)

// 格式化内容
const formattedContent = computed(() => {
  if (!news.value?.content) return ''
  // 将换行符转换为 HTML 段落
  return news.value.content
    .split('\n\n')
    .filter(p => p.trim())
    .map(p => `<p>${p}</p>`)
    .join('')
})

// 检测是否为英文内容
const detectEnglishContent = (text) => {
  if (!text) return false
  const englishChars = (text.match(/[a-zA-Z]/g) || []).length
  const totalChars = text.replace(/\s/g, '').length
  return totalChars > 0 && (englishChars / totalChars) > 0.5
}

// 翻译英文内容为中文
const translateContent = async (text) => {
  if (!text || !detectEnglishContent(text)) return ''

  isEnglishContent.value = true

  try {
    const response = await translateApi.translate({ text: text, target_language: 'zh' })
    return response.data?.data?.translated_text || ''
  } catch (e) {
    console.error('翻译失败:', e)
  }
  return ''
}

// 生成 AI 总结
const generateAiSummary = async (text) => {
  if (!text) return ''

  generatingSummary.value = true
  try {
    const response = await translateApi.summary({ text: text, max_length: 300 })
    aiSummary.value = response.data?.data?.summary || ''
    // 保存到 news 对象
    if (news.value) {
      news.value.ai_summary = aiSummary.value
    }
  } catch (e) {
    console.error('生成摘要失败:', e)
  } finally {
    generatingSummary.value = false
  }
}

// 加载新闻详情
const loadNewsDetail = async () => {
  loading.value = true
  error.value = null

  try {
    const res = await newsApi.getDetail(route.params.id)
    news.value = res.data?.data

    // 检查是否已收藏
    if (news.value.is_favorite !== undefined) {
      isFavorited.value = news.value.is_favorite
    }

    // 如果有内容，进行翻译和总结
    const contentText = news.value.content || news.value.summary || ''

    // 如果是英文内容，自动翻译
    if (detectEnglishContent(contentText)) {
      translatedContent.value = await translateContent(contentText)
    }

    // 如果没有预存的 AI 总结，生成一个新的
    if (!news.value.ai_summary && contentText) {
      await generateAiSummary(contentText)
    } else if (news.value.ai_summary) {
      aiSummary.value = news.value.ai_summary
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || '加载新闻详情失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 返回列表
const goBack = () => {
  router.back()
}

// 打开原始链接
const openOriginal = () => {
  if (news.value?.source_url) {
    window.open(news.value.source_url, '_blank')
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    console.log('toggleFavorite 被调用，news:', news.value)
    console.log('当前收藏状态:', isFavorited.value)
    if (isFavorited.value) {
      console.log('取消收藏，newsId:', news.value.id)
      await favoriteApi.removeByNews(news.value.id)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      console.log('添加收藏，newsId:', news.value.id)
      const payload = { news_id: news.value.id, tags: [] }
      console.log('请求 payload:', payload)
      const res = await favoriteApi.add(payload)
      console.log('收藏响应:', res)
      isFavorited.value = true
      ElMessage.success('已添加到收藏')
    }
  } catch (e) {
    console.error('收藏操作失败，详细错误:', e)
    console.error('错误响应:', e?.response)
    console.error('错误数据:', e?.response?.data)
    ElMessage.error(`操作失败：${e?.response?.data?.detail || e.message}`)
  }
}

// 获取分类标签类型
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

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  console.log('NewsDetail 组件加载，route.params:', route.params)
  loadNewsDetail()
})
</script>

<style scoped>
.news-detail-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.detail-container {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.news-header {
  margin-bottom: 24px;
}

.news-title {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

/* AI 摘要卡片 */
.ai-summary-card {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.ai-summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.ai-icon {
  color: #667eea;
  font-size: 18px;
}

.ai-title {
  font-weight: 600;
  color: #667eea;
  font-size: 15px;
}

.ai-summary-content {
  color: #303133;
  line-height: 1.8;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.8);
  padding: 12px;
  border-radius: 6px;
}

/* 翻译提示 */
.translation-notice {
  margin-bottom: 20px;
}

/* 内容区域 */
.content-section {
  margin-bottom: 24px;
}

.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.original-content,
.translated-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
}

.original-content :deep(p) {
  margin-bottom: 16px;
}

.translated-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.summary-only {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-top: 20px;
}

.summary-text {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

.error-state {
  padding: 40px 0;
}
</style>
