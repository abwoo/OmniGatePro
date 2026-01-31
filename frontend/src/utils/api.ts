import axios from 'axios';

// 优先从 localStorage 获取 API 地址，其次是环境变量，最后是 localhost
const getApiBaseUrl = () => {
  const savedUrl = localStorage.getItem('artfish_api_url');
  if (savedUrl) return savedUrl;
  
  // import.meta.env.VITE_API_URL 可以在构建时注入
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  withCredentials: true,
  timeout: 10000, // 10s 超时
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

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      console.error('Network error or API unreachable:', error);
      // 可以在这里提示用户检查后端是否启动
    }
    return Promise.reject(error);
  }
);

export const setApiUrl = (url: string) => {
  localStorage.setItem('artfish_api_url', url);
  window.location.reload();
};

export default api;
