import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

// 新闻 API
export const newsApi = {
  getList: (params) => api.get('/news/list', { params }),
  getDetail: (id) => api.get(`/news/${id}`),
  getCategories: () => api.get('/news/categories'),
  delete: (id) => api.delete(`/news/${id}`)
}

// 热点 API
export const hotApi = {
  getDaily: (params) => api.get('/hot/daily', { params }),
  getStatistics: (params) => api.get('/hot/statistics', { params }),
  getTrend: (params) => api.get('/hot/trend', { params })
}

// 收藏 API
export const favoriteApi = {
  getList: (params) => api.get('/favorite/list', { params }),
  add: (data) => api.post('/favorite/add', data),
  remove: (id) => api.delete(`/favorite/${id}`),
  removeByNews: (newsId) => api.delete(`/favorite/by_news/${newsId}`),
  updateTags: (id, tags) => api.put(`/favorite/${id}/tags`, { tags }),
  getTags: () => api.get('/favorite/tags')
}

// 信源 API
export const sourceApi = {
  getList: (params) => api.get('/source/list', { params }),
  getDetail: (id) => api.get(`/source/${id}`),
  add: (data) => api.post('/source/add', data),
  update: (id, data) => api.put(`/source/${id}`, data),
  delete: (id) => api.delete(`/source/${id}`),
  getCategories: () => api.get('/source/categories'),
  importExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/source/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  exportExcel: (params) => api.get('/source/export', {
    params,
    responseType: 'blob'
  })
}

// 采集 API
export const crawlApi = {
  run: () => api.post('/crawl/run'),
  status: () => api.get('/crawl/status')
}

// 日志 API
export const logsApi = {
  getRecent: (params) => api.get('/logs/recent', { params }),
  getStatistics: () => api.get('/logs/statistics'),
  getSystem: () => api.get('/logs/system'),
  getFiles: () => api.get('/logs/files')
}

// 翻译 API
export const translateApi = {
  translate: (data) => api.post('/translate/translate', data),
  summary: (data) => api.post('/translate/summary', data),
  detectLanguage: (text) => api.get('/translate/detect-language', { params: { text } })
}

export default api
