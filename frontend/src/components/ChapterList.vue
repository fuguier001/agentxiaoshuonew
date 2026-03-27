<template>
  <el-card class="chapters-card">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <el-button v-if="showCreate" type="primary" size="small" @click="$emit('create')">新建</el-button>
      </div>
    </template>

    <el-input
      v-if="searchable"
      v-model="searchQuery"
      :placeholder="searchPlaceholder"
      size="small"
      clearable
      style="margin-bottom: 10px"
    />

    <el-menu
      :default-active="String(activeChapter)"
      @select="handleSelect"
    >
      <el-menu-item
        v-for="chapter in filteredChapters"
        :key="chapter[keyField]"
        :index="String(chapter[keyField])"
      >
        <StatusTag
          v-if="showStatus"
          :status="chapter.status"
          type="chapter"
          size="small"
          style="margin-right: 8px"
        />
        <span>{{ prefix }}{{ chapter[keyField] }}{{ suffix }}</span>
        <div v-if="chapter.title" class="chapter-title">{{ chapter.title }}</div>
        <div class="chapter-meta">
          <span>{{ formatWordCount(chapter.wordCount || chapter.word_count || 0) }}字</span>
          <span v-if="chapter.updatedAt || chapter.updated_at">{{ formatDate(chapter.updatedAt || chapter.updated_at) }}</span>
        </div>
      </el-menu-item>
    </el-menu>

    <el-empty v-if="filteredChapters.length === 0" :description="emptyText" />
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import StatusTag from './StatusTag.vue'

const props = defineProps({
  chapters: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: '章节列表'
  },
  activeChapter: {
    type: [Number, String],
    default: 1
  },
  keyField: {
    type: String,
    default: 'num'
  },
  prefix: {
    type: String,
    default: '第'
  },
  suffix: {
    type: String,
    default: '章'
  },
  searchable: {
    type: Boolean,
    default: true
  },
  searchPlaceholder: {
    type: String,
    default: '搜索章节...'
  },
  showStatus: {
    type: Boolean,
    default: true
  },
  showCreate: {
    type: Boolean,
    default: true
  },
  emptyText: {
    type: String,
    default: '暂无章节'
  }
})

const emit = defineEmits(['select', 'create'])

const searchQuery = ref('')

const filteredChapters = computed(() => {
  if (!searchQuery.value) return props.chapters
  const query = searchQuery.value.toLowerCase()
  return props.chapters.filter(ch =>
    (ch.title && ch.title.toLowerCase().includes(query)) ||
    String(ch[props.keyField]).includes(query)
  )
})

const handleSelect = (index) => {
  emit('select', parseInt(index))
}

const formatWordCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-title {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}
</style>
