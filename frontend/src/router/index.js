import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/oil-gas',
    name: 'OilGas',
    component: () => import('../views/OilGas.vue'),
    meta: { title: '油气' }
  },
  {
    path: '/wind-power',
    name: 'WindPower',
    component: () => import('../views/WindPower.vue'),
    meta: { title: '风电' }
  },
  {
    path: '/ffml',
    name: 'FFML',
    component: () => import('../views/FFML.vue'),
    meta: { title: 'FFML' }
  },
  {
    path: '/hot',
    name: 'Hot',
    component: () => import('../views/Hot.vue'),
    meta: { title: '热点' }
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/Favorite.vue'),
    meta: { title: '收藏' }
  },
  {
    path: '/source',
    name: 'Source',
    component: () => import('../views/Source.vue'),
    meta: { title: '信源' }
  },
  {
    path: '/news/:id',
    name: 'NewsDetail',
    component: () => import('../views/NewsDetail.vue'),
    meta: { title: '新闻详情' }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title + ' - 热点资讯'
  }
  next()
})

export default router
