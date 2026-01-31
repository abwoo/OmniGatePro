import axios from 'axios';

// 优先使用环境变量，否则回退到 localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// 请求拦截器：自动注入 CSRF Token 和 Auth Token
api.interceptors.request.use((config) => {
  // 从 Cookie 中获取 CSRF Token
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='))
    ?.split('=')[1];

  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }

  // 从 LocalStorage 获取 JWT Token
  const token = localStorage.getItem('artfish_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  return config;
});

export default api;
