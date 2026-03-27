<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ displayText }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'default' // default, novel, chapter, agent
  },
  size: {
    type: String,
    default: 'default'
  },
  effect: {
    type: String,
    default: 'light'
  }
})

// 状态映射
const statusMap = {
  // 通用状态
  default: {
    active: { text: '活跃', type: 'success' },
    inactive: { text: '未激活', type: 'info' },
    pending: { text: '待处理', type: 'warning' },
    error: { text: '错误', type: 'danger' },
    // novel
    ongoing: { text: '连载中', type: 'success' },
    completed: { text: '已完成', type: 'info' },
    paused: { text: '暂停', type: 'warning' },
    cancelled: { text: '已取消', type: 'danger' },
    // chapter
    draft: { text: '草稿', type: 'warning' },
    published: { text: '已发布', type: 'success' },
    archived: { text: '已归档', type: 'info' },
    // agent
    idle: { text: '空闲', type: 'success' },
    working: { text: '工作中', type: 'warning' },
    busy: { text: '忙碌', type: 'danger' }
  },
  novel: {
    ongoing: { text: '连载中', type: 'success' },
    completed: { text: '已完成', type: 'info' },
    paused: { text: '暂停', type: 'warning' },
    cancelled: { text: '已取消', type: 'danger' }
  },
  chapter: {
    draft: { text: '草稿', type: 'warning' },
    published: { text: '已发布', type: 'success' },
    archived: { text: '已归档', type: 'info' }
  },
  agent: {
    idle: { text: '空闲', type: 'success' },
    working: { text: '工作中', type: 'warning' },
    busy: { text: '忙碌', type: 'danger' }
  }
}

const tagType = computed(() => {
  const map = statusMap[props.type] || statusMap.default
  return (map[props.status]?.type || 'info')
})

const displayText = computed(() => {
  const map = statusMap[props.type] || statusMap.default
  return (map[props.status]?.text || props.status)
})
</script>

<style scoped>
</style>
