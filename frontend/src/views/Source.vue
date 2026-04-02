<template>
  <div class="source">
    <h2>信源管理</h2>
    <el-table :data="sourceList" border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="网址" />
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const sourceList = ref([])
</script>
