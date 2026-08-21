import axios from 'axios'

export const http = axios.create({
  baseURL: '/api',
  timeout: 10_000,
  headers: {
    Accept: 'application/json',
  },
})

export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return '请求超时，请检查网络后重试。'
    }
    if (!error.response) {
      return '暂时无法连接校园地图服务。'
    }
    const message = (error.response.data as { message?: unknown } | undefined)?.message
    if (typeof message === 'string' && message.length > 0) {
      return message
    }
  }
  return '加载地图基础数据失败，请稍后重试。'
}

