import axios from 'axios'
import { store } from '../app/store'
import { setCredentials, clearCredentials } from '../features/authSlice'


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

let isRefreshing = false
let failedQueue: {
  resolve: (token: string) => void
  reject: (err: any) => void
}[] = []

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => {
      error ? prom.reject(error) : prom.resolve(token!)
    })
    failedQueue = []
  }

api.interceptors.request.use(config => {
  const token = store.getState().auth.accessToken
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// response interceptor to catch 401s
api.interceptors.response.use(
    response => response,
    error => {
      const originalRequest = error.config
      if (
        error.response?.status === 401 &&
        !originalRequest._retry
      ) {
        const { refreshToken } = store.getState().auth
        if (refreshToken) {
          if (isRefreshing) {
            // queue this request until the token is refreshed
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject })
            }).then(token => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return api(originalRequest)
            })
          }

          originalRequest._retry = true
          isRefreshing = true

          // attempt to get a new pair
          return new Promise((resolve, reject) => {
            axios
              .post(`${import.meta.env.VITE_API_URL}/auth/refresh/`, {
                refresh: refreshToken
              })
              .then(({ data }) => {
                // store the new tokens
                store.dispatch(setCredentials({
                  access: data.access,
                  refresh: data.refresh
                }))
                api.defaults.headers.common.Authorization =
                  `Bearer ${data.access}`
                processQueue(null, data.access)
                resolve(api(originalRequest))
              })
              .catch(err => {
                processQueue(err, null)
                store.dispatch(clearCredentials())
                reject(err)
              })
              .finally(() => {
                isRefreshing = false
              })
          })
        } else {
          // no refresh token: force logout
          store.dispatch(clearCredentials())
        }
      }
      return Promise.reject(error)
    }
  )

export default api
