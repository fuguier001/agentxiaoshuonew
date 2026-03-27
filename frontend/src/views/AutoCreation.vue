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

        <!-- 断点续传提示 -->
        <el-form-item v-if="checkpointStatus.exists">
          <el-alert
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              检测到未完成的创作（{{ checkpointStatus.step_name }}）
            </template>
            <p>上次创作在"{{ checkpointStatus.step_name }}"步骤中断</p>
            <p style="margin-top: 8px;">
              <el-button size="small" type="primary" @click="resumeCreation" :loading="creating">
                继续创作
              </el-button>
              <el-button size="small" @click="deleteCheckpointAndStart" :loading="creating">
                重新开始
              </el-button>
            </p>
          </el-alert>
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

    <!-- 蓝图预览对话框 -->
    <el-dialog
      v-model="blueprintVisible"
      title="📊 小说蓝图详情"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="blueprintActiveTab" type="border-card">
        <!-- 世界观地图 -->
        <el-tab-pane label="🌍 世界观地图" name="worldMap">
          <div v-if="blueprintData.world_map" class="blueprint-section">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="世界名称" :span="2">
                {{ blueprintData.world_map.name || '未命名' }}
              </el-descriptions-item>
              <el-descriptions-item label="世界类型">
                {{ blueprintData.world_map.type || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="力量体系">
                {{ blueprintData.world_map.power_system || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <h4 style="margin-top: 20px;">世界概述</h4>
            <el-input
              :model-value="blueprintData.world_map.description || '暂无描述'"
              type="textarea"
              :rows="6"
              readonly
            />

            <div v-if="blueprintData.world_map.regions?.length" style="margin-top: 20px;">
              <h4>主要区域</h4>
              <el-collapse>
                <el-collapse-item
                  v-for="(region, idx) in blueprintData.world_map.regions"
                  :key="idx"
                  :title="region.name || `区域 ${idx + 1}`"
                >
                  <p>{{ region.description || '暂无描述' }}</p>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
          <el-empty v-else description="暂无世界观数据" />
        </el-tab-pane>

        <!-- 宏观规划 -->
        <el-tab-pane label="📋 章节规划" name="macroPlot">
          <div v-if="blueprintData.macro_plot" class="blueprint-section">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="总章节数">
                {{ blueprintData.macro_plot.total_chapters || displayChapterCount }}
              </el-descriptions-item>
              <el-descriptions-item label="卷数">
                {{ blueprintData.macro_plot.volumes?.length || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="预计字数">
                {{ blueprintData.macro_plot.estimated_words || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="blueprintData.macro_plot.volumes?.length" style="margin-top: 20px;">
              <h4>卷结构</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="(volume, idx) in blueprintData.macro_plot.volumes"
                  :key="idx"
                  :timestamp="`第 ${volume.start_chapter || '?'} - ${volume.end_chapter || '?'} 章`"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ volume.name || `第 ${idx + 1} 卷` }}</h4>
                    <p>{{ volume.description || '暂无描述' }}</p>
                    <el-tag v-if="volume.theme" size="small" style="margin-top: 8px;">
                      {{ volume.theme }}
                    </el-tag>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>

            <div v-if="blueprintData.macro_plot.key_plot_points?.length" style="margin-top: 20px;">
              <h4>关键情节点</h4>
              <el-table :data="blueprintData.macro_plot.key_plot_points" border stripe>
                <el-table-column prop="chapter" label="章节" width="100" />
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getPlotPointType(row.type)">
                      {{ row.type || '普通' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>
          </div>
          <el-empty v-else description="暂无章节规划数据" />
        </el-tab-pane>

        <!-- 人物体系 -->
        <el-tab-pane label="👥 人物体系" name="characters">
          <div v-if="blueprintData.characters?.length" class="blueprint-section">
            <el-row :gutter="20">
              <el-col
                v-for="(char, idx) in blueprintData.characters"
                :key="idx"
                :span="8"
              >
                <el-card class="character-card" shadow="hover">
                  <template #header>
                    <div class="character-header">
                      <span class="character-name">{{ char.name || '未命名' }}</span>
                      <el-tag :type="getCharacterType(char.role)" size="small">
                        {{ char.role || '配角' }}
                      </el-tag>
                    </div>
                  </template>
                  <p class="character-desc">{{ char.description || '暂无描述' }}</p>
                  <div v-if="char.traits?.length" class="character-traits">
                    <el-tag
                      v-for="trait in char.traits"
                      :key="trait"
                      size="small"
                      effect="plain"
                      style="margin: 2px;"
                    >
                      {{ trait }}
                    </el-tag>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          <el-empty v-else description="暂无人物数据" />
        </el-tab-pane>

        <!-- 伏笔网络 -->
        <el-tab-pane label="🎣 伏笔网络" name="hooks">
          <div v-if="blueprintData.hooks?.length" class="blueprint-section">
            <el-table :data="blueprintData.hooks" border stripe>
              <el-table-column prop="name" label="伏笔名称" width="200" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getHookType(row.type)">
                    {{ row.type || '普通' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="plant_chapter" label="埋设章节" width="100" />
              <el-table-column prop="payoff_chapter" label="揭示章节" width="100" />
              <el-table-column prop="description" label="描述" />
            </el-table>

            <div v-if="hookStats" style="margin-top: 20px;">
              <h4>伏笔统计</h4>
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-statistic title="短篇伏笔" :value="hookStats.short" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="中篇伏笔" :value="hookStats.medium" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="长篇伏笔" :value="hookStats.long" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="终极伏笔" :value="hookStats.ultimate" />
                </el-col>
              </el-row>
            </div>
          </div>
          <el-empty v-else description="暂无伏笔数据" />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
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
const blueprintVisible = ref(false)
const overallProgress = ref(0)
const progressStatus = ref(null)
const currentStep = ref(0)

// 断点续传状态
const checkpointStatus = ref({ exists: false })

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

const blueprintActiveTab = ref('worldMap')
const blueprintData = ref({})

const startTime = ref(0)

const displayChapterCount = computed(() => {
  return form.chapter_count === 'custom' ? form.custom_chapter_count : form.chapter_count
})

const hookStats = computed(() => {
  const hooks = blueprintData.value.hooks || []
  return {
    short: hooks.filter(h => h.type === 'short' || h.type === '短篇').length,
    medium: hooks.filter(h => h.type === 'medium' || h.type === '中篇').length,
    long: hooks.filter(h => h.type === 'long' || h.type === '长篇').length,
    ultimate: hooks.filter(h => h.type === 'ultimate' || h.type === '终极').length
  }
})

// 辅助函数：获取情节点类型样式
const getPlotPointType = (type) => {
  const typeMap = {
    '高潮': 'danger',
    '转折': 'warning',
    '伏笔': 'info',
    '爽点': 'success'
  }
  return typeMap[type] || ''
}

// 辅助函数：获取角色类型样式
const getCharacterType = (role) => {
  const roleMap = {
    '主角': 'danger',
    '女主': 'warning',
    '反派': 'info',
    '配角': 'success'
  }
  return roleMap[role] || ''
}

// 辅助函数：获取伏笔类型样式
const getHookType = (type) => {
  const typeMap = {
    '短篇': '',
    '中篇': 'warning',
    '长篇': 'success',
    '终极': 'danger'
  }
  return typeMap[type] || ''
}

// 检查断点状态
const checkCheckpoint = async () => {
  if (!form.title) return

  try {
    const result = await apiClient.auto.getCheckpoint(form.title)
    if (result.data) {
      checkpointStatus.value = result.data
    }
  } catch (error) {
    console.error('检查断点失败:', error)
  }
}

// 监听书名变化，检查断点
watch(() => form.title, (newTitle) => {
  if (newTitle) {
    checkCheckpoint()
  } else {
    checkpointStatus.value = { exists: false }
  }
}, { immediate: true })

// 继续创作（断点续传）
const resumeCreation = async () => {
  creating.value = true
  progressVisible.value = true
  startTime.value = Date.now()

  // 根据断点步骤设置当前进度
  const stepMap = { 'world_map': 1, 'macro_plot': 2, 'character_system': 3, 'hook_network': 4, 'completed': 5 }
  currentStep.value = stepMap[checkpointStatus.value.step_name] || 0

  try {
    const payload = {
      ...form,
      chapter_count: form.chapter_count === 'custom' ? form.custom_chapter_count : form.chapter_count,
      resume: true
    }
    const result = await apiClient.auto.create(payload)

    if (result.data) {
      creationTime.value = Math.round((Date.now() - startTime.value) / 1000)
      resultData.value = result.data

      if (result.data.blueprint) {
        worldMapSummary.value = JSON.stringify(result.data.blueprint.world_map, null, 2).substring(0, 500) + '...'
        macroPlotSummary.value = JSON.stringify(result.data.blueprint.macro_plot, null, 2).substring(0, 500) + '...'
      }

      if (result.data.first_chapter && result.data.first_chapter.content) {
        firstChapterPreview.value = result.data.first_chapter.content.substring(0, 500) + '...'
      }

      overallProgress.value = 100
      progressStatus.value = 'success'
      checkpointStatus.value = { exists: false }

      setTimeout(() => {
        progressVisible.value = false
        resultVisible.value = true
        ElMessage.success('创作完成！')
      }, 1000)
    }
  } catch (error) {
    console.error('继续创作失败:', error)
    handleError(error)
  } finally {
    creating.value = false
  }
}

// 删除断点并重新开始
const deleteCheckpointAndStart = async () => {
  try {
    await apiClient.auto.deleteCheckpoint(form.title)
    checkpointStatus.value = { exists: false }
    ElMessage.success('断点已删除，可以重新开始创作')
  } catch (error) {
    console.error('删除断点失败:', error)
    ElMessage.error('删除断点失败')
  }
}

// 统一错误处理
const handleError = (error) => {
  console.error('创作失败:', error)
  progressStatus.value = 'exception'

  // 检查是否是断点保存的情况
  if (error.response?.status === 202 || error.code === 'CHECKPOINT_SAVED') {
    ElMessage.warning('创作中断，进度已保存。下次可以从断点继续。')
    checkCheckpoint()
  } else if (error.code === 'ECONNABORTED') {
    ElMessage.error('创作请求超时：全自动创作耗时较长，进度已自动保存')
    checkCheckpoint()
  } else {
    const backendMessage = error.response?.data?.error?.message || error.message
    ElMessage.error('创作失败：' + backendMessage)
  }

  setTimeout(() => {
    progressVisible.value = false
  }, 2000)
}

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

  // 启动 SSE 进度监听
  const eventSource = new EventSource(`/api/auto/progress-stream/${encodeURIComponent(form.title)}`)
  eventSource.onmessage = (event) => {
    try {
      const progress = JSON.parse(event.data)
      console.log('进度更新:', progress)

      // 更新当前步骤
      if (progress.step !== undefined) {
        currentStep.value = progress.step
      }

      // 更新步骤描述
      if (progress.step_name && progress.message) {
        // 根据步骤名更新对应的描述
        switch (progress.step_name) {
          case 'world_map':
            worldMapDesc.value = progress.message
            break
          case 'macro_plot':
            macroPlotDesc.value = progress.message
            break
          case 'character_system':
            characterDesc.value = progress.message
            break
          case 'hook_network':
            hookDesc.value = progress.message
            break
          case 'first_chapter':
            chapterDesc.value = progress.message
            break
        }
      }

      // 更新整体进度
      if (progress.status === 'completed') {
        overallProgress.value = 100
        progressStatus.value = 'success'
        eventSource.close()
      } else if (progress.status === 'error') {
        progressStatus.value = 'exception'
        ElMessage.error(progress.message || '创作失败')
        eventSource.close()
      } else if (progress.status === 'generating') {
        // 计算进度百分比
        overallProgress.value = Math.min(90, (progress.step / 5) * 100)
      }
    } catch (e) {
      console.error('解析进度数据失败:', e)
    }
  }

  eventSource.onerror = (error) => {
    console.error('SSE 连接错误:', error)
    eventSource.close()
  }

  try {
    // 调用全自动创作 API
    const payload = {
      ...form,
      chapter_count: form.chapter_count === 'custom' ? form.custom_chapter_count : form.chapter_count
    }
    const result = await apiClient.auto.create(payload)

    // 关闭 SSE
    eventSource.close()
    
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
    eventSource.close()
  }
}

const viewNovel = () => {
  // 跳转到写作面板
  router.push('/writing')
}

const viewBlueprint = () => {
  if (resultData.value.blueprint) {
    blueprintData.value = resultData.value.blueprint
    blueprintActiveTab.value = 'worldMap'
    blueprintVisible.value = true
  } else {
    ElMessage.warning('暂无蓝图数据')
  }
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

/* 蓝图预览样式 */
.blueprint-section {
  padding: 10px 0;
}

.blueprint-section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-weight: 600;
}

.character-card {
  margin-bottom: 20px;
}

.character-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.character-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.character-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.character-traits {
  margin-top: 12px;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}
</style>
