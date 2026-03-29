import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  register: (data) => api.post('/api/auth/register', data),
  refresh: (token) => api.post('/api/auth/refresh', { refresh_token: token }),
  health: () => api.get('/health'),
}

export const transactionsAPI = {
  list: (params) => api.get('/api/transactions/', { params }),
  create: (data) => api.post('/api/transactions/', data),
  get: (id) => api.get(`/api/transactions/${id}`),
}

export const fraudAPI = {
  alerts: (params) => api.get('/api/fraud/alerts', { params }),
  logs: (params) => api.get('/api/fraud/logs', { params }),
  review: (id, data) => api.put(`/api/fraud/review/${id}`, data),
}

export const analyticsAPI = {
  dashboard: () => api.get('/api/analytics/dashboard'),
  trends: () => api.get('/api/analytics/trends'),
}

export default api
