<template>
  <el-container style="height: 100vh;">
    <!-- 左侧栏 -->
    <el-aside width="360px" style="border-right: 1px solid #e4e7ed; overflow-y: auto; padding: 12px; height: 100vh;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <span style="font-size:18px;font-weight:700;color:#303133;">RAG 智能问答</span>
        <el-tooltip :content="`${auth.username} · 退出`">
          <el-button size="small" :icon="SwitchButton" circle @click="handleLogout" />
        </el-tooltip>
      </div>
      <UploadPanel @uploaded="docListRef?.load()" />
      <el-divider />
      <DocList ref="docListRef" />
    </el-aside>

    <!-- 右侧对话区 -->
    <el-main style="padding: 0; display: flex; flex-direction: column;">
      <ChatPanel />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import UploadPanel from '../components/UploadPanel.vue'
import DocList from '../components/DocList.vue'
import ChatPanel from '../components/ChatPanel.vue'

const auth = useAuthStore()
const router = useRouter()
const docListRef = ref<InstanceType<typeof DocList>>()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
