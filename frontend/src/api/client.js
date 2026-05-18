import axios from 'axios'

const client = axios.create({
  baseURL:
    window.__ENV__?.VITE_API_URL ??
    import.meta.env.VITE_API_URL ??
    'http://localhost:8000/api/v1',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function extractUserMessage(error) {
  if (!error.response) {
    return 'Нет соединения с сервером'
  }

  const { status, data } = error.response

  if (status === 422) {
    if (Array.isArray(data?.detail)) {
      return data.detail.map((e) => e.msg.replace('Value error, ', '')).join('; ')
    }
    return data?.detail ?? 'Ошибка валидации данных'
  }

  if (status === 500) {
    return 'Ошибка сервера, попробуйте позже'
  }

  return data?.detail ?? 'Произошла ошибка'
}

client.interceptors.response.use(
  (response) => response,
  (error) => {
    error.userMessage = extractUserMessage(error)

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  },
)

export default client
