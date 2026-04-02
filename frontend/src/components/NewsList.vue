<template>
  <div class="news-list-container">
    <el-row :gutter="20">
      <el-col
        v-for="news in newsList"
        :key="news.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        class="news-item"
      >
        <NewsCard :news="news" @favorite="handleFavorite" />
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty v-if="newsList.length === 0" description="暂无新闻数据" />

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
import NewsCard from './NewsCard.vue'

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
  }
})

const emit = defineEmits(['load', 'favorite'])

const currentPage = ref(1)
const pageSize = ref(20)

// 监听分页变化
watch([currentPage, pageSize], ([newPage, newSize]) => {
  emit('load', { page: newPage, pageSize: newSize })
})

// 处理分页大小变化
const handleSizeChange = (size) => {
  currentPage.value = 1
  emit('load', { page: 1, pageSize: size })
}

// 处理页码变化
const handleCurrentChange = (page) => {
  emit('load', { page, pageSize: pageSize.value })
}

// 处理收藏
const handleFavorite = (news) => {
  emit('favorite', news)
}
</script>

<style scoped>
.news-list-container {
  padding: 20px;
}

.news-item {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px 0;
}
</style>
