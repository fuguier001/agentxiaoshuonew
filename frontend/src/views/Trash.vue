<template>
  <div class="trash-page">
    <h2>🗑️ 回收站</h2>

    <el-alert
      title="回收站说明"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    >
      <p>已删除的小说会保留在回收站中。您可以恢复小说，或从回收站永久删除。</p>
    </el-alert>

    <!-- 小说列表 -->
    <el-row :gutter="20" v-if="novels.length > 0">
      <el-col :span="8" v-for="novel in novels" :key="novel.id">
        <el-card class="trash-card" shadow="hover">
          <template #header>
            <div class="novel-header">
              <span class="novel-title">{{ novel.title }}</span>
              <el-tag size="small" type="info">{{ novel.genre }}</el-tag>
            </div>
          </template>

          <div class="novel-content">
            <p class="novel-desc">{{ novel.description || '暂无简介' }}</p>

            <div class="novel-stats">
              <el-tag size="small" type="info">📖 {{ novel.total_chapters || 0 }}章</el-tag>
              <el-tag size="small" type="success">✍️ {{ formatNumber(novel.total_words || 0) }}字</el-tag>
            </div>

            <div class="novel-meta">
              <span class="delete-time">删除于：{{ formatDate(novel.deleted_at) }}</span>
            </div>
          </div>

          <template #footer>
            <div class="novel-actions">
              <el-button size="small" type="success" @click="restoreNovel(novel.id)">♻️ 恢复</el-button>
              <el-button size="small" type="danger" @click="permanentDelete(novel.id)">🗑️ 永久删除</el-button>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty v-if="novels.length === 0" description="回收站是空的">
      <el-button type="primary" @click="$router.push('/library')">📚 去小说仓库</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiClient } from '@/api/client'

const novels = ref([])

const loadTrash = async () => {
  try {
    const result = await apiClient.trash.list()
    if (result.data && result.data.novels) {
      novels.value = result.data.novels
    }
  } catch (error) {
    ElMessage.error('加载回收站失败：' + error.message)
  }
}

const restoreNovel = async (novelId) => {
  try {
    await ElMessageBox.confirm('确定要恢复这本小说吗？', '恢复确认', {
      confirmButtonText: '确定恢复',
      cancelButtonText: '取消',
      type: 'info'
    })

    await apiClient.trash.restore(novelId)
    ElMessage.success('小说已恢复')
    loadTrash()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败：' + error.message)
    }
  }
}

const permanentDelete = async (novelId) => {
  try {
    await ElMessageBox.confirm(
      '永久删除后无法恢复！确定要彻底删除这本小说吗？',
      '永久删除确认',
      {
        confirmButtonText: '永久删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await apiClient.trash.permanentDelete(novelId)
    ElMessage.success('小说已永久删除')
    loadTrash()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const utcString = dateString.includes('T') ? dateString : dateString.replace(' ', 'T') + 'Z'
  const date = new Date(utcString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadTrash()
})
</script>

<style scoped>
.trash-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.trash-card {
  margin-bottom: 20px;
  border-color: #e6a23c;
}

.novel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.novel-title {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-content {
  min-height: 100px;
}

.novel-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 15px;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.novel-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.novel-meta {
  font-size: 12px;
  color: #999;
}

.delete-time {
  color: #e6a23c;
}

.novel-actions {
  display: flex;
  gap: 10px;
}
</style>
