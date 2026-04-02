<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>热点资讯</h1>
        <el-menu mode="horizontal" :router="true" :default-active="$route.path">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/oil">油气</el-menu-item>
          <el-menu-item index="/wind">风电</el-menu-item>
          <el-menu-item index="/ffml">FFML</el-menu-item>
          <el-menu-item index="/hot">热点</el-menu-item>
          <el-menu-item index="/favorite">收藏</el-menu-item>
          <el-menu-item index="/source">信源</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
#app {
  font-family: Arial, sans-serif;
}
.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.el-header h1 {
  margin: 10px 0;
}
.el-menu {
  width: 100%;
  background-color: #409EFF;
}
.el-menu-item {
  color: white !important;
}
.el-menu-item.is-active {
  background-color: #66b1ff !important;
}
.el-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}
</style>
