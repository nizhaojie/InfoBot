<template>
  <div class="doc-list">
    <div class="toolbar">
      <span class="section-title">文档管理</span>
      <el-button size="small" @click="load" :loading="loading">刷新</el-button>
    </div>

    <el-table
      :data="docs"
      size="small"
      @selection-change="selected = $event"
      style="width:100%"
    >
      <el-table-column type="selection" width="36" />
      <el-table-column prop="source" label="文件名 / URL" show-overflow-tooltip />
      <el-table-column prop="chunk_count" label="块数" width="55" />
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      small
      @current-change="load"
      style="margin-top:6px"
    />

    <div class="del-row">
      <el-button
        type="danger"
        size="small"
        :disabled="selected.length === 0"
        @click="deleteSelected"
      >
        删除选中 ({{ selected.length }})
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchDocuments, deleteDocuments } from '../api/index'

const docs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const selected = ref<any[]>([])

async function load() {
  loading.value = true
  try {
    const res = await fetchDocuments(page.value, pageSize)
    docs.value = res.data.items
    total.value = res.data.total
  } catch {
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

async function deleteSelected() {
  await ElMessageBox.confirm(`确认删除选中的 ${selected.value.length} 个来源及其所有向量数据？`, '提示', { type: 'warning' })
  const sources = selected.value.map((d) => d.source)
  await deleteDocuments(sources)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
defineExpose({ load })
</script>

<style scoped>
.doc-list { padding: 8px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.section-title { font-weight: 600; color: #303133; }
.del-row { margin-top: 8px; text-align: right; }
</style>
