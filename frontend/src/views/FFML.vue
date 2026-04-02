<template>
  <div class="ffml">
    <h2>FFML 资讯</h2>
    <el-table :data="newsList" border>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="date" label="日期" />
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const newsList = ref([])
</script>
