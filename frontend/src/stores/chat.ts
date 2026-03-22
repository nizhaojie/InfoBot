import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Message {
  role: 'user' | 'assistant'
  content: string
  loading?: boolean  // 流式输出中
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const sessionId = ref(`session_${Date.now()}`)

  function addUserMessage(content: string) {
    messages.value.push({ role: 'user', content })
  }

  function addAssistantMessage(): number {
    messages.value.push({ role: 'assistant', content: '', loading: true })
    return messages.value.length - 1
  }

  function appendToken(index: number, token: string) {
    messages.value[index].content += token
  }

  function finishMessage(index: number) {
    messages.value[index].loading = false
  }

  function clearHistory() {
    messages.value = []
    sessionId.value = `session_${Date.now()}`
  }

  return { messages, sessionId, addUserMessage, addAssistantMessage, appendToken, finishMessage, clearHistory }
})
