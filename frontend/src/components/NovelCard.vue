<template>
  <el-card class="novel-card" shadow="hover">
    <template #header>
      <div class="novel-header">
        <el-checkbox
          v-if="selectable"
          v-model="selected"
          :label="novel.id"
          @click.stop
        />
        <span class="novel-title">{{ novel.title }}</span>
        <el-tag size="small" type="success">{{ novel.genre }}</el-tag>
      </div>
    </template>

    <div class="novel-content">
      <p class="novel-desc">{{ novel.description || '暂无简介' }}</p>

      <div class="novel-stats">
        <el-tag size="small" type="info">📖 {{ novel.total_chapters || 0 }}章</el-tag>
        <el-tag size="small" type="success">✍️ {{ formatNumber(novel.total_words || 0) }}字</el-tag>
      </div>

      <div class="novel-meta">
        <StatusTag :status="novel.status" type="novel" size="small" />
        <span class="create-time">创建：{{ formatDate(novel.created_at) }}</span>
      </div>
    </div>

    <template #footer>
      <div class="novel-actions">
        <el-button size="small" type="primary" @click="$emit('view', novel.id)">📖 查看</el-button>
        <el-button size="small" type="success" @click="$emit('edit', novel.id)">✏️ 编辑</el-button>
        <el-button size="small" type="warning" @click="$emit('continue', novel.id)">✍️ 续写</el-button>
        <el-button size="small" type="info" @click="$emit('download', novel.id)">📥 下载</el-button>
        <el-button size="small" type="danger" @click="$emit('delete', novel.id)">🗑️ 删除</el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import StatusTag from './StatusTag.vue'

const props = defineProps({
  novel: {
    type: Object,
    required: true
  },
  selectable: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view', 'edit', 'continue', 'download', 'delete', 'update:modelValue'])

const selected = computed({
  get: () => props.modelValue.includes(props.novel.id),
  set: (val) => {
    const newValue = [...props.modelValue]
    if (val && !newValue.includes(props.novel.id)) {
      newValue.push(props.novel.id)
    } else if (!val) {
      const index = newValue.indexOf(props.novel.id)
      if (index > -1) {
        newValue.splice(index, 1)
      }
    }
    emit('update:modelValue', newValue)
  }
})

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  // 后端返回的是 UTC 时间，需要添加 Z 后缀正确解析
  const utcString = dateString.includes('T') ? dateString : dateString.replace(' ', 'T') + 'Z'
  const date = new Date(utcString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.novel-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.novel-card:hover {
  transform: translateY(-5px);
}

.novel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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
  min-height: 150px;
}

.novel-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 15px;
  height: 60px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.create-time {
  margin-left: 10px;
}

.novel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
