<template>
  <div class="upload-panel">
    <div class="section-title">上传文件</div>
    <el-upload
      drag
      multiple
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      accept=".pdf,.txt,.md,.markdown"
      :file-list="fileList"
      class="compact-upload"
    >
      <el-icon style="font-size:20px"><upload-filled /></el-icon>
      <div style="font-size:12px;margin-top:4px">拖拽或 <em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">PDF / TXT / Markdown，可多选</div>
      </template>
    </el-upload>

    <el-button
      v-if="fileList.length"
      type="primary"
      style="margin-top:8px;width:100%"
      :loading="uploadingFile"
      @click="doUpload"
    >
      导入全部 ({{ fileList.length }})
    </el-button>

    <el-divider />

    <div class="section-title">导入网页</div>
    <el-input v-model="urlInput" placeholder="输入网页 URL" clearable />
    <el-button
      type="primary"
      style="margin-top:8px;width:100%"
      :loading="uploadingUrl"
      @click="doUploadUrl"
    >
      抓取并导入
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadSource } from '../api/index'

const emit = defineEmits(['uploaded'])

const fileList = ref<any[]>([])
const urlInput = ref('')
const uploadingFile = ref(false)
const uploadingUrl = ref(false)

function handleFileChange(file: any, list: any[]) {
  fileList.value = list
}

function handleFileRemove(_file: any, list: any[]) {
  fileList.value = list
}

async function doUpload() {
  if (!fileList.value.length) return
  uploadingFile.value = true
  let successCount = 0
  for (const f of fileList.value) {
    try {
      const fd = new FormData()
      fd.append('file', f.raw)
      await uploadSource(fd)
      successCount++
    } catch (e: any) {
      ElMessage.error(`${f.name} 上传失败：${e.response?.data?.detail || '未知错误'}`)
    }
  }
  if (successCount) {
    ElMessage.success(`成功导入 ${successCount} 个文件`)
    fileList.value = []
    emit('uploaded')
  }
  uploadingFile.value = false
}

async function doUploadUrl() {
  const url = urlInput.value.trim()
  if (!url) return
  uploadingUrl.value = true
  try {
    const fd = new FormData()
    fd.append('url', url)
    const res = await uploadSource(fd)
    ElMessage.success(res.data.message)
    urlInput.value = ''
    emit('uploaded')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    uploadingUrl.value = false
  }
}
</script>

<style scoped>
.upload-panel { padding: 8px; }
.section-title { font-weight: 600; margin-bottom: 8px; color: #303133; }
.compact-upload :deep(.el-upload-dragger) {
  padding: 12px;
  height: auto;
}
</style>
