// frontend/src/services/authService.js
import axios from 'axios'

// 配置API基础URL
const API_URL = '/api/auth'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 登录方法
export async function login(credentials) {
  try {
    const response = await axios.post(`${API_URL}/login`, {
      username: credentials.username,
      password: credentials.password
    })

    // 存储token和用户信息
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))

    return response.data
  } catch (error) {
    throw error
  }
}

// 注册方法
export async function register(userData) {
  try {
    const response = await axios.post(`${API_URL}/register`, {
      username: userData.username,
      email: userData.email,
      password: userData.password
    })
    return response.data
  } catch (error) {
    throw error
  }
}

// 检查用户是否已登录
export function isAuthenticated() {
  const token = localStorage.getItem('token')
  return !!token
}

// 获取当前用户信息
export function getCurrentUser() {
  const userStr = localStorage.getItem('user')
  if (!userStr) return null
  return JSON.parse(userStr)
}

// 退出登录
export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}