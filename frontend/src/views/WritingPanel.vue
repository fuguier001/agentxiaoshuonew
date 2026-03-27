<template>
  <div class="writing-panel">
    <h2>✍️ 写作面板</h2>
    
    <!-- 顶部：小说选择 -->
    <el-card class="novel-selector-card">
      <el-form :inline="true">
        <el-form-item label="选择小说">
          <el-select 
            v-model="selectedNovelId" 
            placeholder="选择要创作的小说"
            style="width: 300px"
            @change="loadNovelData"
          >
            <el-option
              v-for="novel in novels"
              :key="novel.id"
              :label="novel.title"
              :value="novel.id"
            >
              <span>{{ novel.title }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ novel.chapterCount }}章</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="createNewNovel">新建小说</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="editNovelSettings">小说设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- AI 创作工具 -->
    <el-card class="ai-tools-card" v-if="selectedNovelId">
      <template #header>
        <div class="card-header">
          <span>🤖 AI 创作工具</span>
          <div>
            <el-button type="success" size="small" @click="showAiOutlineGen">生成大纲</el-button>
            <el-button type="success" size="small" @click="showAiCharactersGen">生成人物</el-button>
            <el-button type="success" size="small" @click="showAiChapterOutline">生成章节大纲</el-button>
            <el-button type="success" size="small" @click="showAiPlotDesign">生成情节</el-button>
          </div>
        </div>
      </template>
      <el-alert
        title="AI 创作说明"
        type="info"
        :closable="false"
        show-icon
      >
        <p>所有创作内容都由 AI 生成，你只需要：</p>
        <ul>
          <li>点击"生成大纲" → AI 为你生成小说整体大纲</li>
          <li>点击"生成人物" → AI 为你设计所有角色</li>
          <li>点击"生成章节大纲" → AI 为当前章节生成详细大纲</li>
          <li>点击"生成情节" → AI 设计本章情节发展</li>
          <li>最后点击"AI 创作" → AI 撰写完整章节正文</li>
        </ul>
      </el-alert>
    </el-card>
    
    <el-row :gutter="20" v-if="selectedNovelId">
      <!-- 左侧：章节列表 -->
      <el-col :span="6">
        <ChapterList
          :chapters="chapters"
          :active-chapter="currentChapterNum"
          @select="handleChapterSelect"
          @create="createNewChapter"
        />

        <!-- 统计信息 -->
        <el-card class="stats-card" style="margin-top: 20px">
          <template #header>统计信息</template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="总章节数">{{ totalChapters }}</el-descriptions-item>
            <el-descriptions-item label="总字数">{{ totalWords.toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="已发布">{{ publishedChapters }}</el-descriptions-item>
            <el-descriptions-item label="草稿">{{ draftChapters }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <!-- 中间：创作区域 -->
      <el-col :span="12">
        <el-card class="editor-card">
          <template #header>
            <div class="card-header">
              <el-input
                v-model="chapterTitle"
                placeholder="章节标题"
                size="large"
                style="flex: 1; margin-right: 10px"
              />
              <el-button 
                type="primary" 
                @click="startWriting" 
                :loading="writing"
                size="large"
              >
                {{ writing ? '创作中...' : 'AI 创作' }}
              </el-button>
            </div>
          </template>
          
          <!-- 大纲编辑区 -->
          <div class="outline-section">
            <div class="section-header">
              <span>📋 本章大纲</span>
              <el-tag size="small" type="info">给 AI 的创作指令</el-tag>
            </div>
            <el-input
              v-model="chapterOutline"
              type="textarea"
              :rows="6"
              placeholder="请输入本章大纲，例如：主角首次遭遇反派，展现两人性格对比。需要包含冲突、对话和动作描写。"
              resize="vertical"
            />
          </div>
          
          <el-divider />
          
          <!-- 正文编辑区 -->
          <div class="content-section">
            <div class="section-header">
              <span>📝 正文内容</span>
              <div class="section-actions">
                <el-radio-group v-model="editorMode" size="small">
                  <el-radio-button label="edit">编辑</el-radio-button>
                  <el-radio-button label="preview">预览</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            
            <el-input
              v-if="editorMode === 'edit'"
              v-model="chapterContent"
              type="textarea"
              :rows="20"
              placeholder="在此输入或编辑正文内容..."
              resize="vertical"
            />
            
            <div v-else class="preview-content" v-html="renderedContent"></div>
            
            <div class="content-footer">
              <span class="word-count">
                字数：{{ currentWordCount }} / 目标：{{ wordCountTarget }}
                <el-progress 
                  :percentage="Math.min(100, (currentWordCount / wordCountTarget) * 100)" 
                  :status="currentWordCount >= wordCountTarget ? 'success' : undefined"
                  style="width: 150px; margin-left: 10px"
                />
              </span>
              <div class="actions">
                <el-button @click="saveChapter" :disabled="!chapterContent">保存</el-button>
                <el-button @click="exportChapter">导出</el-button>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 创作设置 -->
        <el-card class="settings-card" style="margin-top: 20px">
          <template #header>创作设置</template>
          <el-form label-width="100px" size="small">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="章节号">
                  <el-input-number v-model="currentChapterNum" :min="1" :max="10000" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="目标字数">
                  <el-input-number v-model="wordCountTarget" :min="500" :max="10000" :step="500" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="写作风格">
              <el-select v-model="selectedStyle" placeholder="选择风格" style="width: 100%" @change="showStylePreview">
                <el-option label="默认风格" value="default" />
                <el-option
                  v-for="style in availableStyles"
                  :key="style.id"
                  :label="style.name"
                  :value="style.id"
                />
              </el-select>
              <div v-if="stylePreview" class="style-preview">
                <el-alert :title="stylePreview.name" type="info" :closable="false" show-icon>
                  <p>{{ stylePreview.description }}</p>
                  <p><strong>特点：</strong>{{ stylePreview.features.join('、') }}</p>
                </el-alert>
              </div>
            </el-form-item>
            
            <el-form-item label="应用技巧">
              <el-checkbox-group v-model="selectedTechniques">
                <el-checkbox 
                  v-for="tech in availableTechniques" 
                  :key="tech.id" 
                  :label="tech.id"
                >
                  {{ tech.name }}
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 右侧：辅助面板 -->
      <el-col :span="6">
        <!-- Agent 状态 -->
        <AgentStatusCard :agents="agentStatus" />
        
        <!-- 人物提示 -->
        <el-card class="characters-card" style="margin-top: 20px">
          <template #header>本章人物</template>
          <el-tag
            v-for="char in chapterCharacters"
            :key="char.id"
            closable
            @close="removeCharacter(char.id)"
            style="margin: 3px"
          >
            {{ char.name }}
          </el-tag>
          <el-button size="small" text @click="addCharacter" style="margin-top: 5px">
            + 添加人物
          </el-button>
        </el-card>
        
        <!-- 伏笔提示 -->
        <el-card class="hooks-card" style="margin-top: 20px">
          <template #header>
            <span>伏笔提示</span>
            <el-badge :value="unresolvedHooks" :hidden="unresolvedHooks === 0" type="warning" />
          </template>
          <el-empty v-if="unresolvedHooks === 0" description="暂无未回收伏笔" />
          <div v-else class="hook-list">
            <div v-for="hook in unresolvedHookList" :key="hook.id" class="hook-item">
              <el-tag size="small" type="warning">{{ hook.type }}</el-tag>
              <p>{{ hook.description }}</p>
              <small>第{{ hook.chapterIntroduced }}章埋设</small>
            </div>
          </div>
        </el-card>
        
        <!-- Token 统计 -->
        <el-card class="token-stats-card" style="margin-top: 20px">
          <template #header>API 使用统计</template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="今日调用">{{ todayCalls }}</el-descriptions-item>
            <el-descriptions-item label="Token 消耗">{{ tokenUsed.toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="估算费用">¥{{ estimatedCost.toFixed(2) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 创作日志 -->
        <el-card class="log-card" style="margin-top: 20px">
          <template #header>
            <span>创作日志</span>
            <el-switch v-model="autoScroll" active-text="自动滚动" size="small" />
          </template>
          <div class="log-container" ref="logContainer">
            <div v-for="(log, index) in logs" :key="index" class="log-item">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-empty v-else description="请先选择要创作的小说" :image-size="200" />
    
    <!-- 创作进度对话框 -->
    <el-dialog v-model="progressVisible" title="AI 创作中" width="600px" :close-on-click-modal="false">
      <el-progress :percentage="progress" :status="progressStatus" />
      <p style="text-align: center; margin-top: 10px">{{ currentStage }}</p>
      
      <el-steps direction="vertical" :active="currentStep" style="margin-top: 20px">
        <el-step title="剧情架构师" description="细化大纲" />
        <el-step title="人物设计师" description="准备角色" />
        <el-step title="章节写手" description="撰写初稿" />
        <el-step title="对话专家" description="打磨对话" />
        <el-step title="审核编辑" description="一致性检查" />
        <el-step title="主编" description="最终审核" />
      </el-steps>
    </el-dialog>
    
    <!-- 版本历史对话框 -->
    <el-dialog v-model="versionVisible" title="版本历史" width="700px">
      <el-timeline>
        <el-timeline-item
          v-for="version in versions"
          :key="version.id"
          :timestamp="version.createdAt"
          placement="top"
        >
          <el-card>
            <h4>版本 {{ version.version }}</h4>
            <p>字数：{{ version.wordCount }}</p>
            <p v-if="version.note">备注：{{ version.note }}</p>
            <el-button size="small" @click="previewVersion(version)">预览</el-button>
            <el-button size="small" type="primary" @click="restoreVersion(version)">恢复</el-button>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
    
    <!-- 新建小说对话框 -->
    <el-dialog v-model="newNovelVisible" title="新建小说" width="500px">
      <el-form :model="newNovelForm" label-width="80px">
        <el-form-item label="小说标题">
          <el-input v-model="newNovelForm.title" placeholder="请输入小说标题" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="newNovelForm.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="玄幻" value="fantasy" />
            <el-option label="武侠" value="wuxia" />
            <el-option label="言情" value="romance" />
            <el-option label="悬疑" value="mystery" />
            <el-option label="都市" value="urban" />
            <el-option label="历史" value="history" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="newNovelForm.description" type="textarea" :rows="4" placeholder="小说简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newNovelVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateNovel">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 小说设置对话框 -->
    <el-dialog v-model="settingsVisible" title="小说设置" width="500px">
      <el-form :model="novelSettings" label-width="80px">
        <el-form-item label="小说标题">
          <el-input v-model="novelSettings.title" placeholder="小说标题" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="novelSettings.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="玄幻" value="fantasy" />
            <el-option label="武侠" value="wuxia" />
            <el-option label="言情" value="romance" />
            <el-option label="悬疑" value="mystery" />
            <el-option label="都市" value="urban" />
            <el-option label="历史" value="history" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="novelSettings.description" type="textarea" :rows="4" placeholder="小说简介" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="novelSettings.status" style="width: 100%">
            <el-option label="连载中" value="ongoing" />
            <el-option label="已完成" value="completed" />
            <el-option label="暂停" value="paused" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settingsVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpdateNovel">保存</el-button>
      </template>
    </el-dialog>

    <!-- 人物选择器对话框 -->
    <el-dialog v-model="characterSelectorVisible" title="选择人物" width="600px">
      <el-form :inline="true" style="margin-bottom: 15px">
        <el-form-item label="搜索">
          <el-input v-model="characterSearch" placeholder="搜索人物名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadNovelCharacters">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="filteredNovelCharacters"
        style="width: 100%"
        max-height="300"
        @selection-change="handleCharacterSelection"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getRoleTagType(row.role)">
              {{ row.role || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>

      <template #footer>
        <el-button @click="characterSelectorVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddCharacters">添加所选</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { apiClient } from '@/api/client'
import ChapterList from '@/components/ChapterList.vue'
import AgentStatusCard from '@/components/AgentStatusCard.vue'

// ========== 小说管理 ==========
const selectedNovelId = ref('')
const novels = ref([])
const newNovelVisible = ref(false)
const settingsVisible = ref(false)
const newNovelForm = reactive({
  title: '',
  genre: 'fantasy',
  description: ''
})
const novelSettings = reactive({
  title: '',
  genre: 'fantasy',
  description: '',
  status: 'ongoing'
})

// ========== 章节管理 ==========
const chapters = ref([])
const currentChapterNum = ref(1)
const chapterTitle = ref('')
const chapterOutline = ref('')
const chapterContent = ref('')
const editorMode = ref('edit')

// ========== 创作设置 ==========
const wordCountTarget = ref(3000)
const selectedStyle = ref('default')
const selectedTechniques = ref([])
const stylePreview = ref(null)

// ========== 状态显示 ==========
const agentStatus = ref([])
const chapterCharacters = ref([])
const unresolvedHooks = ref(0)
const unresolvedHookList = ref([])
const todayCalls = ref(0)
const tokenUsed = ref(0)
const estimatedCost = ref(0)

// ========== 人物选择器 ==========
const characterSelectorVisible = ref(false)
const characterSearch = ref('')
const novelCharacters = ref([])
const selectedCharactersForAdd = ref([])

// ========== 创作流程 ==========
const writing = ref(false)
const progressVisible = ref(false)
const progress = ref(0)
const progressStatus = ref(null)
const currentStage = ref('')
const currentStep = ref(0)
const logs = ref([])
const autoScroll = ref(true)

// ========== 版本管理 ==========
const versionVisible = ref(false)
const versions = ref([])

// ========== 计算属性 ==========
const currentWordCount = computed(() => chapterContent.value.length)

const totalChapters = computed(() => chapters.value.length)

const totalWords = computed(() => 
  chapters.value.reduce((sum, ch) => sum + (ch.wordCount || 0), 0)
)

const publishedChapters = computed(() => 
  chapters.value.filter(ch => ch.status === 'published').length
)

const draftChapters = computed(() => 
  chapters.value.filter(ch => ch.status === 'draft').length
)

const renderedContent = computed(() => {
  return marked(chapterContent.value || '')
})

const availableStyles = ref([
  { id: 'wuxia_jinyong', name: '金庸派' },
  { id: 'wuxia_gulong', name: '古龙派' },
  { id: 'romance_qiongyao', name: '琼瑶派' }
])

const availableTechniques = ref([
  { id: 'multi_thread', name: '多线交织' },
  { id: 'suspense', name: '悬念设置' },
  { id: 'contrast', name: '反差塑造' },
  { id: 'foreshadowing', name: '伏笔千里' },
  { id: 'pacing', name: '节奏控制' }
])

// ========== 人物选择器计算属性 ==========
const filteredNovelCharacters = computed(() => {
  if (!characterSearch.value) return novelCharacters.value
  const search = characterSearch.value.toLowerCase()
  return novelCharacters.value.filter(char =>
    char.name.toLowerCase().includes(search) ||
    (char.role && char.role.toLowerCase().includes(search))
  )
})

// ========== 方法 ==========

const loadNovels = async () => {
  try {
    const result = await apiClient.novels.list()
    if (result.data && result.data.novels) {
      novels.value = result.data.novels.map(novel => ({
        ...novel,
        chapterCount: novel.total_chapters || 0
      }))
    }
  } catch (error) {
    console.error('加载小说列表失败:', error)
    ElMessage.error('加载小说列表失败：' + error.message)
  }
}

const createNewNovel = () => {
  newNovelVisible.value = true
}

const confirmCreateNovel = async () => {
  if (!newNovelForm.title) {
    ElMessage.warning('请输入小说标题')
    return
  }
  
  try {
    const result = await apiClient.novels.create({
      title: newNovelForm.title,
      genre: newNovelForm.genre,
      description: newNovelForm.description
    })
    
    ElMessage.success('小说创建成功')
    newNovelVisible.value = false
    // 重置表单
    newNovelForm.title = ''
    newNovelForm.genre = 'fantasy'
    newNovelForm.description = ''
    
    // 重新加载小说列表
    await loadNovels()
  } catch (error) {
    ElMessage.error('创建失败：' + error.message)
  }
}

const editNovelSettings = async () => {
  if (!selectedNovelId.value) {
    ElMessage.warning('请先选择小说')
    return
  }
  
  try {
    const result = await apiClient.novels.get(selectedNovelId.value)
    if (result.data) {
      const novel = result.data
      novelSettings.title = novel.title
      novelSettings.genre = novel.genre || 'fantasy'
      novelSettings.description = novel.description || ''
      novelSettings.status = novel.status || 'ongoing'
      settingsVisible.value = true
    }
  } catch (error) {
    ElMessage.error('获取小说信息失败：' + error.message)
  }
}

const confirmUpdateNovel = async () => {
  if (!novelSettings.title) {
    ElMessage.warning('请输入小说标题')
    return
  }
  
  try {
    await apiClient.novels.update(selectedNovelId.value, {
      title: novelSettings.title,
      genre: novelSettings.genre,
      description: novelSettings.description,
      status: novelSettings.status
    })
    
    ElMessage.success('小说信息已更新')
    settingsVisible.value = false
    await loadNovels()
  } catch (error) {
    ElMessage.error('更新失败：' + error.message)
  }
}

const loadNovelData = async () => {
  if (!selectedNovelId.value) return
  
  addLog(`加载小说：${selectedNovelId.value}`)
  await loadChapters()
  await loadCharacters()
  await loadHooks()
  await loadNovelStats()
  
  // 保存到 localStorage
  saveCurrentState()
}

const saveCurrentState = () => {
  const state = {
    selectedNovelId: selectedNovelId.value,
    currentChapterNum: currentChapterNum.value,
    chapterTitle: chapterTitle.value,
    chapterOutline: chapterOutline.value,
    chapterContent: chapterContent.value,
    wordCountTarget: wordCountTarget.value,
    selectedStyle: selectedStyle.value,
    timestamp: Date.now()
  }
  localStorage.setItem('writing_panel_state', JSON.stringify(state))
}

const restoreState = () => {
  const saved = localStorage.getItem('writing_panel_state')
  if (saved) {
    try {
      const state = JSON.parse(saved)
      // 检查是否是同一本小说
      if (state.selectedNovelId && novels.value.find(n => n.id === state.selectedNovelId)) {
        selectedNovelId.value = state.selectedNovelId
        currentChapterNum.value = state.currentChapterNum || 1
        chapterTitle.value = state.chapterTitle || ''
        chapterOutline.value = state.chapterOutline || ''
        chapterContent.value = state.chapterContent || ''
        wordCountTarget.value = state.wordCountTarget || 3000
        selectedStyle.value = state.selectedStyle || 'default'
        addLog(`已恢复上次创作状态`)
        
        // 加载小说数据
        loadNovelData()
      }
    } catch (e) {
      console.error('恢复状态失败:', e)
    }
  }
}

const loadChapters = async () => {
  try {
    const result = await apiClient.novels.getChapters(selectedNovelId.value)
    if (result.data && result.data.chapters) {
      chapters.value = result.data.chapters.map(ch => ({
        num: ch.chapter_num,
        title: ch.title || `第${ch.chapter_num}章`,
        status: ch.status || 'draft',
        wordCount: ch.word_count || 0,
        updatedAt: ch.updated_at
      }))
    }
  } catch (error) {
    console.error('加载章节失败:', error)
    ElMessage.error('加载章节失败：' + error.message)
  }
}

const createNewChapter = async () => {
  try {
    const newNum = Math.max(0, ...chapters.value.map(c => c.num)) + 1
    
    // 调用 API 创建章节
    const result = await apiClient.novels.createChapter(selectedNovelId.value, {
      chapter_num: newNum,
      title: '',
      outline: ''
    })
    
    currentChapterNum.value = newNum
    chapterTitle.value = ''
    chapterOutline.value = ''
    chapterContent.value = ''
    
    // 刷新章节列表
    await loadChapters()
    addLog(`创建新章节：第${newNum}章`)
    ElMessage.success('章节创建成功')
  } catch (error) {
    ElMessage.error('创建章节失败：' + error.message)
  }
}

const handleChapterSelect = async (index) => {
  const num = parseInt(index)
  currentChapterNum.value = num
  
  try {
    const result = await apiClient.novels.getChapter(selectedNovelId.value, num)
    if (result.data) {
      const chapter = result.data
      chapterTitle.value = chapter.title || `第${num}章`
      chapterOutline.value = chapter.outline || ''
      chapterContent.value = chapter.content || ''
      addLog(`加载章节：第${num}章 (${chapter.word_count || 0}字)`)
    }
  } catch (error) {
    console.error('加载章节失败:', error)
    ElMessage.error('加载章节失败：' + error.message)
  }
}

const startWriting = async () => {
  if (!chapterOutline.value) {
    ElMessage.warning('请先输入本章大纲')
    return
  }
  
  if (!selectedNovelId.value) {
    ElMessage.warning('请先选择小说')
    return
  }
  
  writing.value = true
  progressVisible.value = true
  progress.value = 0
  currentStep.value = 0
  currentStage.value = '开始创作流程...'
  
  addLog(`开始创作第${currentChapterNum.value}章`)
  
  try {
    // 调用真实的 AI 创作 API
    const result = await apiClient.writing.createChapter({
      novel_id: selectedNovelId.value,
      chapter_num: currentChapterNum.value,
      outline: chapterOutline.value,
      word_count_target: wordCountTarget.value,
      style: selectedStyle.value
    })
    
    if (result.data && result.data.content) {
      // 创作成功，直接显示内容
      progress.value = 100
      progressStatus.value = 'success'
      currentStage.value = '创作完成！'
      addLog('✅ 章节创作完成')
      ElMessage.success('章节创作完成！')
      
      chapterContent.value = result.data.content
      chapterTitle.value = chapterTitle.value || `第${currentChapterNum.value}章`
      addLog(`生成字数：${result.data.word_count || chapterContent.value.length}字`)
      
      // 自动保存
      await saveChapter()
      
      setTimeout(() => {
        progressVisible.value = false
      }, 2000)
    } else {
      // 创作失败
      progressStatus.value = 'exception'
      currentStage.value = result.message || '创作失败'
      addLog('❌ 创作失败：' + result.message)
      ElMessage.error(result.message || '创作失败')
      
      setTimeout(() => {
        progressVisible.value = false
      }, 2000)
    }
  } catch (error) {
    progressStatus.value = 'exception'
    currentStage.value = '创作失败'
    addLog('❌ 创作失败：' + error.message)
    ElMessage.error('创作失败：' + error.message)
    
    setTimeout(() => {
      progressVisible.value = false
    }, 2000)
  } finally {
    writing.value = false
  }
}

const saveChapter = async () => {
  try {
    const result = await apiClient.novels.updateChapter(selectedNovelId.value, currentChapterNum.value, {
      content: chapterContent.value,
      title: chapterTitle.value,
      outline: chapterOutline.value,
      status: 'draft'
    })
    if (result.data) {
      chapterTitle.value = result.data.title || chapterTitle.value
      chapterOutline.value = result.data.outline || chapterOutline.value
      chapterContent.value = result.data.content || chapterContent.value
    }
    addLog(`保存章节：第${currentChapterNum.value}章 (${currentWordCount.value}字)`)
    ElMessage.success('章节已保存')
    
    // 刷新章节列表
    await loadChapters()
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const exportChapter = () => {
  const blob = new Blob([chapterContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `第${currentChapterNum.value}章 - ${chapterTitle.value || '无题'}.txt`
  a.click()
  URL.revokeObjectURL(url)
  addLog(`导出章节：第${currentChapterNum.value}章`)
}

const showStylePreview = () => {
  const style = availableStyles.value.find(s => s.id === selectedStyle.value)
  if (style) {
    stylePreview.value = {
      name: style.name,
      description: `${style.name}的写作风格`,
      features: ['特色 1', '特色 2', '特色 3']
    }
  } else {
    stylePreview.value = null
  }
}

const addCharacter = () => {
  if (!selectedNovelId.value) {
    ElMessage.warning('请先选择小说')
    return
  }
  characterSelectorVisible.value = true
  selectedCharactersForAdd.value = []
  loadNovelCharacters()
}

const loadNovelCharacters = async () => {
  try {
    const result = await apiClient.novels.getCharacters(selectedNovelId.value)
    if (result.data && result.data.characters) {
      novelCharacters.value = result.data.characters.map(c => ({
        id: c.id,
        name: c.name,
        role: c.role || 'unknown',
        description: c.description || ''
      }))
    }
  } catch (error) {
    console.error('加载小说人物列表失败:', error)
    ElMessage.error('加载人物列表失败')
  }
}

const handleCharacterSelection = (selection) => {
  selectedCharactersForAdd.value = selection
}

const confirmAddCharacters = () => {
  if (selectedCharactersForAdd.value.length === 0) {
    ElMessage.warning('请选择要添加的人物')
    return
  }

  for (const char of selectedCharactersForAdd.value) {
    const exists = chapterCharacters.value.find(c => c.id === char.id)
    if (!exists) {
      chapterCharacters.value.push({
        id: char.id,
        name: char.name,
        role: char.role
      })
    }
  }

  ElMessage.success(`已添加 ${selectedCharactersForAdd.value.length} 个人物`)
  characterSelectorVisible.value = false
}

const getRoleTagType = (role) => {
  if (!role) return 'info'
  const roleMap = {
    'protagonist': 'danger',
    'main': 'danger',
    'antagonist': 'warning',
    'villain': 'warning',
    'supporting': 'success',
    'secondary': 'success',
    'minor': 'info'
  }
  return roleMap[role.toLowerCase()] || 'info'
}

const removeCharacter = (id) => {
  chapterCharacters.value = chapterCharacters.value.filter(c => c.id !== id)
}

const loadCharacters = async () => {
  try {
    const result = await apiClient.novels.getCharacters(selectedNovelId.value)
    if (result.data && result.data.characters) {
      chapterCharacters.value = result.data.characters.map(c => ({
        id: c.id,
        name: c.name,
        role: c.role
      }))
    }
  } catch (error) {
    console.error('加载人物失败:', error)
  }
}

const loadHooks = async () => {
  try {
    const result = await apiClient.novels.getHooks(selectedNovelId.value)
    if (result.data && result.data.hooks) {
      unresolvedHooks.value = result.data.total
      unresolvedHookList.value = result.data.hooks.map(h => ({
        id: h.id,
        description: h.description,
        type: h.hook_type,
        chapterIntroduced: h.chapter_introduced
      }))
    }
  } catch (error) {
    console.error('加载伏笔失败:', error)
  }
}

const loadNovelStats = async () => {
  try {
    const result = await apiClient.novels.get(selectedNovelId.value)
    if (result.data && result.data.stats) {
      const stats = result.data.stats
      todayCalls.value = 15 // 这个需要后端实现 API 调用统计
      tokenUsed.value = stats.total_words || 0
      estimatedCost.value = (stats.total_words || 0) * 0.00001 // 估算
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const addLog = (message) => {
  logs.value.push({
    time: new Date().toLocaleTimeString(),
    message
  })
  
  if (logs.value.length > 100) {
    logs.value.shift()
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

// 自动保存 + 持久化
let autoSaveTimer = null
watch([selectedNovelId, currentChapterNum, chapterTitle, chapterOutline, chapterContent, wordCountTarget, selectedStyle], () => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    // 保存到 localStorage
    saveCurrentState()
    
    // 如果有内容，保存到数据库
    if (chapterContent.value || chapterOutline.value) {
      saveChapter()
      addLog('自动保存成功')
    }
  }, 5000) // 5 秒自动保存
}, { deep: true })

onMounted(() => {
  loadNovels()
  addLog('写作面板已就绪')
  
  // 恢复上次的状态
  setTimeout(() => {
    restoreState()
  }, 500)
  
  // 定时刷新 Agent 状态
  setInterval(async () => {
    try {
      const result = await apiClient.agents.getStatus()
      if (result.data && result.data.agents) {
        agentStatus.value = result.data.agents.map(a => ({
          name: a.agent_id.replace('_agent', ''),
          status: a.state
        }))
      }
    } catch (error) {
      console.error('加载 Agent 状态失败:', error)
    }
  }, 5000)
})
</script>

<style scoped>
.writing-panel {
  max-width: 1800px;
  margin: 0 auto;
}

.novel-selector-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.outline-section, .content-section {
  margin-bottom: 15px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.word-count {
  display: flex;
  align-items: center;
  color: #666;
}

.actions {
  display: flex;
  gap: 10px;
}

.style-preview {
  margin-top: 10px;
}

.hook-item {
  margin-bottom: 10px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}

.hook-item p {
  margin: 5px 0;
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.log-item {
  margin-bottom: 5px;
  display: flex;
  gap: 10px;
}

.log-time {
  color: #909399;
  white-space: nowrap;
}

.log-message {
  color: #333;
}

.preview-content {
  min-height: 400px;
  padding: 15px;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 4px;
  line-height: 1.8;
}

.stats-card, .characters-card, .hooks-card, .token-stats-card, .log-card {
  font-size: 13px;
}
</style>
