import axios from 'axios'

// Axios設定
axios.defaults.baseURL = import.meta.env.VITE_API_URL || ''

// リクエストインターセプター
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API関数
export const api = {
  // プロジェクト
  projects: {
    list: () => axios.get('/api/projects'),
    get: (id) => axios.get(`/api/projects/${id}`),
    create: (data) => axios.post('/api/projects', data),
    update: (id, data) => axios.put(`/api/projects/${id}`, data),
    delete: (id) => axios.delete(`/api/projects/${id}`)
  },

  // 課題
  issues: {
    list: (projectId) => axios.get(`/api/projects/${projectId}/issues`),
    get: (id) => axios.get(`/api/issues/${id}`),
    create: (data) => axios.post('/api/issues', data),
    update: (id, data) => axios.put(`/api/issues/${id}`, data),
    delete: (id) => axios.delete(`/api/issues/${id}`)
  },

  // コメント
  comments: {
    list: (issueId) => axios.get(`/api/issues/${issueId}/comments`),
    create: (data) => axios.post('/api/comments', data),
    update: (id, data) => axios.put(`/api/comments/${id}`, data),
    delete: (id) => axios.delete(`/api/comments/${id}`)
  },

  // マイルストーン
  milestones: {
    list: (projectId) => axios.get(`/api/projects/${projectId}/milestones`),
    create: (data) => axios.post('/api/milestones', data),
    update: (id, data) => axios.put(`/api/milestones/${id}`, data),
    delete: (id) => axios.delete(`/api/milestones/${id}`)
  },

  // カテゴリ
  categories: {
    list: (projectId) => axios.get(`/api/projects/${projectId}/categories`),
    create: (data) => axios.post('/api/categories', data),
    update: (id, data) => axios.put(`/api/categories/${id}`, data),
    delete: (id) => axios.delete(`/api/categories/${id}`)
  },

  // Wiki
  wiki: {
    list: (projectId) => axios.get(`/api/projects/${projectId}/wiki`),
    get: (id) => axios.get(`/api/wiki/${id}`),
    create: (data) => axios.post('/api/wiki', data),
    update: (id, data) => axios.put(`/api/wiki/${id}`, data),
    delete: (id) => axios.delete(`/api/wiki/${id}`)
  },

  // ダッシュボード
  dashboard: {
    get: () => axios.get('/api/dashboard')
  },

  // ユーザー
  users: {
    list: () => axios.get('/api/users')
  },

  // 依存関係
  dependencies: {
    list: (projectId) => axios.get(`/api/projects/${projectId}/dependencies`),
    create: (data) => axios.post('/api/dependencies', data),
    delete: (id) => axios.delete(`/api/dependencies/${id}`)
  }
}

export default api
