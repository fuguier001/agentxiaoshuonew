<template>
  <div class="auto-creation">
    <h2>🤖 全自动 AI 创作</h2>
    
    <el-alert
      title="一键创作完整小说"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    >
      <p>你只需要提供：</p>
      <ul>
        <li>✅ 书名</li>
        <li>✅ 类型</li>
        <li>✅ 一句话简介</li>
      </ul>
      <p>AI 会自动生成：</p>
      <ul>
        <li>✅ 完整世界观地图（大地图包小地图）</li>
        <li>✅ 3000 章宏观规划（节奏/爽点/伏笔）</li>
        <li>✅ 人物体系（主角 + 配角 + 反派）</li>
        <li>✅ 伏笔网络（短/中/长/终极）</li>
        <li>✅ 第一章正文（3000 字）</li>
      </ul>
    </el-alert>
    
    <!-- 创作表单 -->
    <el-card class="creation-form-card">
      <template #header>
        <div class="card-header">
          <span>📝 基本信息</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px" size="large">
        <el-form-item label="书名" required>
          <el-input 
            v-model="form.title" 
            placeholder="例如：都市修仙、绝世武神"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="类型" required>
          <el-select v-model="form.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="玄幻" value="玄幻" />
            <el-option label="仙侠" value="仙侠" />
            <el-option label="都市" value="都市" />
            <el-option label="历史" value="历史" />
            <el-option label="科幻" value="科幻" />
            <el-option label="游戏" value="游戏" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="简介" required>
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="用一句话描述小说核心设定，例如：一个普通大学生意外获得修仙传承，在都市中修炼成长，最终登临巅峰"
          />
        </el-form-item>
        
        <el-form-item label="预计篇幅">
          <el-select v-model="form.chapter_count" style="width: 100%">
            <el-option label="1000 章 (短篇)" :value="1000" />
            <el-option label="2000 章 (中篇)" :value="2000" />
            <el-option label="3000 章 (长篇)" :value="3000" />
            <el-option label="5000 章 (超长篇)" :value="5000" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.chapter_count === 'custom'" label="自定义章节数" required>
          <el-input-number
            v-model="form.custom_chapter_count"
            :min="1"
            :max="10000"
            :step="100"
            controls-position="right"
            placeholder="请输入章节数"
            style="width: 100%"
          />
          <div style="margin-top: 8px; color: #909399; font-size: 13px;">
            请输入计划创作的总章节数，建议范围 100 ~ 5000 章。
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            @click="startCreation" 
            :loading="creating"
            style="width: 100%"
          >
            {{ creating ? 'AI 创作中...' : '🚀 开始全自动创作' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 创作进度 -->
    <el-dialog 
      v-model="progressVisible" 
      title="AI 创作中" 
      width="700px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <el-progress 
        :percentage="overallProgress" 
        :status="progressStatus"
        :stroke-width="20"
      />
      
      <el-steps direction="vertical" :active="currentStep" style="margin-top: 30px">
        <el-step 
          title="🌍 生成世界观地图" 
          :description="worldMapDesc"
        />
        <el-step 
          :title="`📋 生成 ${displayChapterCount} 章规划`" 
          :description="macroPlotDesc"
        />
        <el-step 
          title="👥 生成人物体系" 
          :description="characterDesc"
        />
        <el-step 
          title="🎣 生成伏笔网络" 
          :description="hookDesc"
        />
        <el-step 
          title="✍️ 创作第一章" 
          :description="chapterDesc"
        />
      </el-steps>
      
      <div class="progress-tips">
        <el-alert
          title="创作提示"
          type="info"
          :closable="false"
          show-icon
        >
          <p>• AI 正在使用专业模板进行创作</p>
          <p>• 整个过程约需 2-5 分钟</p>
          <p>• 请勿关闭页面</p>
        </el-alert>
      </div>
    </el-dialog>
    
    <!-- 创作结果 -->
    <el-dialog 
      v-model="resultVisible" 
      title="🎉 创作完成" 
      width="900px"
    >
      <el-result
        icon="success"
        title="创作成功"
        :sub-title="`小说《${resultData.novel?.title || form.title}》已创作完成！`"
      >
        <template #extra>
          <el-button type="primary" @click="viewNovel">查看小说</el-button>
          <el-button @click="viewBlueprint">查看蓝图</el-button>
        </template>
      </el-result>
      
      <el-divider />
      
      <h3>📊 生成统计</h3>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="小说 ID">
          {{ resultData.novel_id }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          {{ form.genre }}
        </el-descriptions-item>
        <el-descriptions-item label="预计篇幅">
          {{ form.chapter_count === 'custom' ? `自定义：${form.custom_chapter_count}` : form.chapter_count }}章
        </el-descriptions-item>
        <el-descriptions-item label="创作时间">
          {{ creationTime }}秒
        </el-descriptions-item>
      </el-descriptions>
      
      <h3>🌍 世界观概览</h3>
      <el-input
        v-model="worldMapSummary"
        type="textarea"
        :rows="6"
        readonly
      />
      
      <h3>📋 章节规划</h3>
      <el-input
        v-model="macroPlotSummary"
        type="textarea"
        :rows="6"
        readonly
      />
      
      <h3>✍️ 第一章预览</h3>
      <el-input
        v-model="firstChapterPreview"
        type="textarea"
        :rows="10"
        readonly
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiClient } from '@/api/client'

const router = useRouter()

const form = reactive({
  title: '',
  genre: '玄幻',
  description: '',
  chapter_count: 3000,
  custom_chapter_count: 3000
})

const creating = ref(false)
const progressVisible = ref(false)
const resultVisible = ref(false)
const overallProgress = ref(0)
const progressStatus = ref(null)
const currentStep = ref(0)

const worldMapDesc = ref('等待开始...')
const macroPlotDesc = ref('等待开始...')
const characterDesc = ref('等待开始...')
const hookDesc = ref('等待开始...')
const chapterDesc = ref('等待开始...')

const resultData = ref({})
const creationTime = ref(0)
const worldMapSummary = ref('')
const macroPlotSummary = ref('')
const firstChapterPreview = ref('')

const startTime = ref(0)

const displayChapterCount = computed(() => {
  return form.chapter_count === 'custom' ? form.custom_chapter_count : form.chapter_count
})

const startCreation = async () => {
  // 验证输入
  if (!form.title) {
    ElMessage.warning('请输入书名')
    return
  }
  if (!form.description) {
    ElMessage.warning('请输入简介')
    return
  }
  if (form.chapter_count === 'custom' && (!form.custom_chapter_count || form.custom_chapter_count < 1)) {
    ElMessage.warning('请输入有效的自定义章节数')
    return
  }
  if (form.chapter_count === 'custom' && form.custom_chapter_count > 10000) {
    ElMessage.warning('自定义章节数不能超过 10000 章')
    return
  }
  
  creating.value = true
  progressVisible.value = true
  startTime.value = Date.now()
  
  try {
    // 调用全自动创作 API
    const payload = {
      ...form,
      chapter_count: form.chapter_count === 'custom' ? form.custom_chapter_count : form.chapter_count
    }
    const result = await apiClient.auto.create(payload)
    
    if (result.data) {
      // 计算创作时间
      creationTime.value = Math.round((Date.now() - startTime.value) / 1000)
      
      // 保存结果
      resultData.value = result.data
      
      // 提取摘要
      if (result.data.blueprint) {
        worldMapSummary.value = JSON.stringify(result.data.blueprint.world_map, null, 2).substring(0, 500) + '...'
        macroPlotSummary.value = JSON.stringify(result.data.blueprint.macro_plot, null, 2).substring(0, 500) + '...'
      }
      
      if (result.data.first_chapter && result.data.first_chapter.content) {
        firstChapterPreview.value = result.data.first_chapter.content.substring(0, 500) + '...'
      }
      
      // 完成
      overallProgress.value = 100
      progressStatus.value = 'success'
      
      setTimeout(() => {
        progressVisible.value = false
        resultVisible.value = true
        ElMessage.success('创作完成！')
      }, 1000)
    } else {
      throw new Error(result.message || '创作失败')
    }
  } catch (error) {
    console.error('创作失败:', error)
    progressStatus.value = 'exception'
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('创作请求超时：全自动创作耗时较长，请稍后查看后端日志或重新尝试')
    } else {
      const backendMessage = error.response?.data?.error?.message
      ElMessage.error('创作失败：' + (backendMessage || error.message))
    }
    
    setTimeout(() => {
      progressVisible.value = false
    }, 2000)
  } finally {
    creating.value = false
  }
}

const viewNovel = () => {
  // 跳转到写作面板
  router.push('/writing')
}

const viewBlueprint = () => {
  ElMessage.info('蓝图查看功能开发中...')
}
</script>

<style scoped>
.auto-creation {
  max-width: 1000px;
  margin: 0 auto;
}

.creation-form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-tips {
  margin-top: 20px;
}

.progress-tips ul {
  margin: 10px 0;
  padding-left: 20px;
}

:deep(.el-step__description) {
  font-size: 13px;
  line-height: 1.6;
}

:deep(.el-result__title) {
  font-size: 20px;
}

:deep(.el-result__sub-title) {
  font-size: 14px;
}
</style>
