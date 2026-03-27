<template>
  <el-card shadow="hover" class="stat-card">
    <!-- 字符串值（如状态图标） -->
    <div v-if="isStringValue" class="stat-string-value">
      <div class="stat-title">{{ title }}</div>
      <div class="stat-value">
        <span class="value-main">{{ value }}</span>
        <span v-if="suffix" class="value-suffix">{{ suffix }}</span>
      </div>
    </div>
    <!-- 数值类型使用 el-statistic -->
    <el-statistic v-else :title="title" :value="value">
      <template v-if="prefix" #prefix>{{ prefix }}</template>
      <template v-if="suffix" #suffix>{{ suffix }}</template>
    </el-statistic>
    <div v-if="trend" class="stat-trend" :class="trendClass">
      <span>{{ trend > 0 ? '↑' : '↓' }}</span>
      <span>{{ Math.abs(trend) }}%</span>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  trend: {
    type: Number,
    default: null
  }
})

const isStringValue = computed(() => {
  return typeof props.value === 'string'
})

const trendClass = computed(() => {
  if (props.trend === null) return ''
  return props.trend > 0 ? 'trend-up' : 'trend-down'
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  cursor: default;
}

.stat-string-value {
  text-align: center;
}

.stat-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.value-main {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.value-suffix {
  font-size: 14px;
  color: #606266;
}

.stat-trend {
  margin-top: 8px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}
</style>
