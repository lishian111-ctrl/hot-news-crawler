import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

const newsApi = {
  // 获取新闻列表
  getNewsList: (params) => api.get('/news', { params }),
  // 获取新闻详情
  getNewsDetail: (id) => api.get(`/news/${id}`),
  // 获取热点排行
  getHotRanking: (params) => api.get('/hot/rank', { params }),
  // 获取每日热点
  getHotNews: (params) => api.get('/hot/news', { params }),
  // 收藏相关
  toggleFavorite: (id) => api.post(`/favorite/toggle/${id}`),
  removeFavorite: (id) => api.delete(`/favorite/${id}`),
  getFavoriteList: (params) => api.get('/favorite', { params }),
  batchRemoveFavorite: (ids) => api.post('/favorite/batch-remove', { ids })
}

export default newsApi
