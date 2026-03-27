<template>
  <el-card class="agent-status-card">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <el-button
          v-if="refreshable"
          size="small"
          text
          @click="$emit('refresh')"
        >
          🔄 刷新
        </el-button>
      </div>
    </template>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="agents.length === 0" class="empty-state">
      <el-empty :description="emptyText" :image-size="60" />
    </div>

    <div v-else class="agent-list">
      <div
        v-for="agent in agents"
        :key="agent.id || agent.name"
        class="agent-item"
      >
        <StatusTag
          :status="agent.status || agent.state"
          type="agent"
          size="small"
        />
        <span class="agent-name">{{ formatAgentName(agent.name || agent.agent_id) }}</span>
        <el-tooltip
          v-if="agent.task"
          :content="agent.task"
          placement="top"
        >
          <el-icon class="task-icon"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <div v-if="showSummary" class="agent-summary">
      <el-divider />
      <el-descriptions :column="2" size="small">
        <el-descriptions-item label="空闲">
          <el-tag type="success" size="small">{{ idleCount }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="工作中">
          <el-tag type="warning" size="small">{{ workingCount }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Loading, InfoFilled } from '@element-plus/icons-vue'
import StatusTag from './StatusTag.vue'

const props = defineProps({
  agents: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Agent 状态'
  },
  loading: {
    type: Boolean,
    default: false
  },
  refreshable: {
    type: Boolean,
    default: false
  },
  showSummary: {
    type: Boolean,
    default: true
  },
  emptyText: {
    type: String,
    default: '暂无 Agent 信息'
  }
})

const emit = defineEmits(['refresh'])

const formatAgentName = (name) => {
  if (!name) return 'Unknown'
  // 移除 _agent 后缀并格式化
  return name.replace('_agent', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const idleCount = computed(() => {
  return props.agents.filter(a => (a.status || a.state) === 'idle').length
})

const workingCount = computed(() => {
  return props.agents.filter(a => (a.status || a.state) === 'working').length
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #909399;
}

.empty-state {
  padding: 10px 0;
}

.agent-list {
  max-height: 300px;
  overflow-y: auto;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.agent-name {
  flex: 1;
}

.task-icon {
  color: #909399;
  cursor: pointer;
}

.agent-summary {
  margin-top: 10px;
}
</style>
