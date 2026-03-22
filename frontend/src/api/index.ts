/**
 * API 请求封装
 * - axios 实例用于普通请求（自动注入 JWT）
 * - fetchSSE 用于 SSE 流式对话（POST + ReadableStream）
 */
import axios from 'axios'

export const http = axios.create({ baseURL: '/api' })

// 请求拦截器：自动注入 Authorization header
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：401 时清除 token 并跳转登录
http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

/** 上传文件或 URL */
export function uploadSource(formData: FormData) {
  return http.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取文档列表 */
export function fetchDocuments(page = 1, pageSize = 20) {
  return http.get('/documents', { params: { page, page_size: pageSize } })
}

/** 删除文档（按来源列表） */
export function deleteDocuments(sources: string[]) {
  return http.delete('/documents', { data: { sources } })
}

/**
 * SSE 流式对话
 * @param question 用户问题
 * @param sessionId 会话 ID
 * @param onToken 每收到一个 token 的回调
 * @param onDone 完成回调
 */
export async function streamChat(
  question: string,
  sessionId: string,
  onToken: (token: string) => void,
  onDone: () => void,
) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}),
    },
    body: JSON.stringify({ question, session_id: sessionId }),
  })

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    // 按 SSE 行分割处理
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const json = line.slice(6).trim()
      if (!json) continue
      const data = JSON.parse(json)
      if (data.done) {
        onDone()
      } else if (data.token) {
        onToken(data.token)
      }
    }
  }
}
