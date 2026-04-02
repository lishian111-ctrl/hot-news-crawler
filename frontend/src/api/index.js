import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 新闻 API
export const newsApi = {
  // 获取新闻列表
  getList: (params) => api.get('/news', { params }),
  // 获取新闻详情
  getDetail: (id) => api.get(`/news/${id}`),
  // 搜索新闻
  search: (params) => api.get('/news/search', { params })
}

// 热点 API
export const hotApi = {
  // 获取热点列表
  getList: (params) => api.get('/hot', { params }),
  // 获取热点排行
  getRank: () => api.get('/hot/rank')
}

// 收藏 API
export const favoriteApi = {
  // 获取收藏列表
  getList: (params) => api.get('/favorite', { params }),
  // 添加收藏
  add: (data) => api.post('/favorite', data),
  // 删除收藏
  delete: (id) => api.delete(`/favorite/${id}`),
  // 检查是否已收藏
  check: (newsId) => api.get(`/favorite/check/${newsId}`)
}

// 信源 API
export const sourceApi = {
  // 获取信源列表
  getList: (params) => api.get('/source', { params }),
  // 添加信源
  add: (data) => api.post('/source', data),
  // 更新信源
  update: (id, data) => api.put(`/source/${id}`, data),
  // 删除信源
  delete: (id) => api.delete(`/source/${id}`),
  // 获取信源详情
  getDetail: (id) => api.get(`/source/${id}`)
}

export default api
