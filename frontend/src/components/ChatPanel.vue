<template>
  <div class="chat-panel">
    <!-- 消息列表 -->
    <div ref="msgListRef" class="msg-list">
      <div v-if="store.messages.length === 0" class="empty-hint">
        请在左侧上传文档，然后在此处提问
      </div>
      <div
        v-for="(msg, i) in store.messages"
        :key="i"
        :class="['msg-item', msg.role]"
      >
        <el-avatar :icon="msg.role === 'user' ? 'User' : 'ChatDotRound'" size="small" />
        <div class="bubble">
          <!-- 流式输出时显示光标 -->
          <span>{{ msg.content }}</span>
          <span v-if="msg.loading" class="cursor">▌</span>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入问题，按 Ctrl+Enter 发送"
        :disabled="isLoading"
        @keydown.ctrl.enter="sendMessage"
      />
      <div class="btn-row">
        <el-button @click="store.clearHistory" :disabled="isLoading" size="small">清空对话</el-button>
        <el-button type="primary" @click="sendMessage" :loading="isLoading">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { streamChat } from '../api/index'

const store = useChatStore()
const inputText = ref('')
const isLoading = ref(false)
const msgListRef = ref<HTMLElement>()

// 消息更新时自动滚动到底部
watch(() => store.messages.length, async () => {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
})

async function sendMessage() {
  const question = inputText.value.trim()
  if (!question || isLoading.value) return

  inputText.value = ''
  isLoading.value = true
  store.addUserMessage(question)
  const idx = store.addAssistantMessage()

  // 滚动到底部
  await nextTick()
  if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight

  try {
    await streamChat(
      question,
      store.sessionId,
      (token) => {
        store.appendToken(idx, token)
        // 流式输出时持续滚动
        if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
      },
      () => store.finishMessage(idx),
    )
  } catch (e) {
    store.appendToken(idx, '\n[请求失败，请检查后端服务]')
    store.finishMessage(idx)
    ElMessage.error('对话请求失败')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.empty-hint {
  text-align: center;
  color: #999;
  margin-top: 40px;
}
.msg-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.msg-item.user {
  flex-direction: row-reverse;
}
.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
.msg-item.user .bubble {
  background: #409eff;
  color: #fff;
}
.msg-item.assistant .bubble {
  background: #f4f4f5;
  color: #303133;
}
.cursor {
  animation: blink 0.8s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
.input-area {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
}
.btn-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
</style>
