<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <h2>欢迎使用多 Agent 协作小说系统</h2>
      <p>这是一个会学习、会进化、越写越好的 AI 小说创作系统。</p>

      <h3>核心特性</h3>
      <ul>
        <li>🤖 7 大 Agent 协作：主编、剧情、人物、写手、对话、审核、学习</li>
        <li>🧠 三层记忆系统：短期 + 中期 + 长期记忆</li>
        <li>📖 四层学习记忆：原始→模式→技巧→风格</li>
        <li>🏛️ 派系分类系统：按类型/文笔/节奏分类，支持融合</li>
        <li>🔌 可配置 LLM：智谱/火山/阿里云/eggfans 完全可配置</li>
        <li>💾 本地保存：自动保存 + Git 版本控制</li>
      </ul>

      <h3>快速开始</h3>
      <ol>
        <li>前往 <strong>项目配置</strong> 页面配置 LLM API 密钥</li>
        <li>在 <strong>学习中心</strong> 上传喜欢的小说进行学习</li>
        <li>在 <strong>派系库</strong> 选择或融合写作风格</li>
        <li>在 <strong>写作面板</strong> 开始创作你的小说</li>
      </ol>
    </el-card>

    <el-divider />

    <h3>📊 系统状态</h3>
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <StatsCard
          title="API 状态"
          :value="apiStatus === '正常' ? '✅' : '❌'"
          :suffix="apiStatus"
        />
      </el-col>
      <el-col :span="6">
        <StatsCard title="Agent 数量" :value="agentCount" suffix="个" />
      </el-col>
      <el-col :span="6">
        <StatsCard title="项目数量" :value="stats.projectCount" suffix="本" />
      </el-col>
      <el-col :span="6">
        <StatsCard title="章节总数" :value="stats.chapterCount" suffix="章" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <StatsCard title="总字数" :value="stats.totalWords" suffix="字" />
      </el-col>
      <el-col :span="6">
        <StatsCard title="已学习作品" :value="stats.learnedWorks" suffix="部" />
      </el-col>
      <el-col :span="6">
        <StatsCard title="派系数量" :value="stats.schoolCount" suffix="个" />
      </el-col>
      <el-col :span="6">
        <StatsCard title="今日 API 调用" :value="stats.todayCalls" suffix="次" />
      </el-col>
    </el-row>

    <el-divider />

    <h3>🚀 快捷操作</h3>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/auto')">
          <div class="action-content">
            <span class="action-icon">🤖</span>
            <span class="action-title">全自动创作</span>
            <span class="action-desc">一键生成完整小说</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/writing')">
          <div class="action-content">
            <span class="action-icon">✍️</span>
            <span class="action-title">写作面板</span>
            <span class="action-desc">手动创作章节</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/learning')">
          <div class="action-content">
            <span class="action-icon">📚</span>
            <span class="action-title">学习中心</span>
            <span class="action-desc">上传作品学习风格</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/config')">
          <div class="action-content">
            <span class="action-icon">⚙️</span>
            <span class="action-title">项目配置</span>
            <span class="action-desc">配置 LLM 提供商</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '@/api/client'
import { StatsCard } from '@/components'

const router = useRouter()

const apiStatus = ref('检查中...')
const agentCount = ref(7)

const stats = reactive({
  projectCount: 0,
  chapterCount: 0,
  totalWords: 0,
  learnedWorks: 0,
  schoolCount: 0,
  todayCalls: 0
})

const checkApiStatus = async () => {
  try {
    const response = await fetch('/api/ping')
    if (response.ok) {
      apiStatus.value = '正常'
    } else {
      apiStatus.value = '异常'
    }
  } catch (error) {
    apiStatus.value = '不可达'
  }
}

const loadStats = async () => {
  try {
    // 加载小说统计
    const novelsResult = await apiClient.novels.list()
    if (novelsResult.data && novelsResult.data.novels) {
      stats.projectCount = novelsResult.data.novels.length

      // 统计章节和字数
      let totalChapters = 0
      let totalWords = 0
      for (const novel of novelsResult.data.novels) {
        totalChapters += novel.total_chapters || 0
        totalWords += novel.total_words || 0
      }
      stats.chapterCount = totalChapters
      stats.totalWords = totalWords
    }

    // 加载学习作品统计
    try {
      const learningResult = await apiClient.learning.getWorks()
      if (learningResult.data && learningResult.data.works) {
        stats.learnedWorks = learningResult.data.total || learningResult.data.works.length
      }
    } catch (e) {
      // 学习 API 可能不存在
    }

    // 加载派系统计
    try {
      const schoolsResult = await apiClient.schools.list()
      if (schoolsResult.data && schoolsResult.data.schools) {
        stats.schoolCount = schoolsResult.data.total || schoolsResult.data.schools.length
      }
    } catch (e) {
      // 派系 API 可能不存在
    }

    // 加载 Agent 状态
    try {
      const agentsResult = await apiClient.agents.getStatus()
      if (agentsResult.data && agentsResult.data.agents) {
        agentCount.value = agentsResult.data.total || agentsResult.data.agents.length
      }
    } catch (e) {
      // Agent API 可能不存在
    }

  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  checkApiStatus()
  loadStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

ul, ol {
  line-height: 2;
}

h3 {
  margin-top: 20px;
  margin-bottom: 15px;
}

.stats-row {
  margin-bottom: 20px;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.action-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.action-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}
</style>
