import axios from 'axios'
import { store } from '../app/store'

console.log('🔗 API baseURL =', import.meta.env.VITE_API_URL)
// … your axios.create({ baseURL: import.meta.env.VITE_API_URL }) …

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.request.use(config => {
  const token = store.getState().auth.accessToken
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
