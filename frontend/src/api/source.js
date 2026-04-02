import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

const sourceApi = {
  // 获取信源列表
  getSourceList: (params) => api.get('/source', { params }),
  // 获取信源详情
  getSourceDetail: (id) => api.get(`/source/${id}`),
  // 添加信源
  addSource: (data) => api.post('/source', data),
  // 更新信源
  updateSource: (id, data) => api.put(`/source/${id}`, data),
  // 删除信源
  deleteSource: (id) => api.delete(`/source/${id}`)
}

export default sourceApi
