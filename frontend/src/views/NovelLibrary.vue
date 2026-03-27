<template>
  <div class="novel-library">
    <h2>📚 小说仓库</h2>
    
    <!-- 批量操作工具栏 -->
    <el-card class="batch-card" v-if="selectedNovels.length > 0">
      <div class="batch-toolbar">
        <span class="batch-info">已选择 {{ selectedNovels.length }} 本小说</span>
        <div class="batch-actions">
          <el-button type="warning" size="small" @click="batchDownload">📥 批量下载</el-button>
          <el-button type="danger" size="small" @click="batchDelete">🗑️ 批量删除</el-button>
          <el-button size="small" @click="clearSelection">❌ 取消选择</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input v-model="searchQuery" placeholder="搜索书名..." clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterGenre" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="玄幻" value="玄幻" />
            <el-option label="仙侠" value="仙侠" />
            <el-option label="都市" value="都市" />
            <el-option label="历史" value="历史" />
            <el-option label="科幻" value="科幻" />
            <el-option label="游戏" value="游戏" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="连载中" value="ongoing" />
            <el-option label="已完成" value="completed" />
            <el-option label="暂停" value="paused" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadNovels">🔄 刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 小说列表 -->
    <el-row :gutter="20" v-show="paginatedNovels.length > 0">
      <el-col :span="8" v-for="novel in paginatedNovels" :key="novel.id">
        <NovelCard
          :novel="novel"
          :selectable="true"
          v-model="selectedNovels"
          @view="viewNovel"
          @edit="editNovel"
          @continue="continueWriting"
          @download="startDownload"
          @delete="deleteNovel"
        />
      </el-col>
    </el-row>
    
    <!-- 分页 -->
    <el-pagination
      v-show="totalPages > 1"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="filteredNovels.length"
      layout="total, prev, pager, next"
      style="margin-top: 20px; justify-content: center; display: flex;"
    />
    
    <!-- 空状态 -->
    <el-empty v-show="novels.length === 0" description="暂无小说，快去创作吧！">
      <el-button type="primary" @click="$router.push('/auto')">🚀 开始创作</el-button>
    </el-empty>

    <!-- 查看对话框（Tabs 结构） -->
    <el-dialog v-model="viewVisible" title="📖 查看小说" width="1000px" top="5vh">
      <div v-if="selectedNovel">
        <!-- 小说基本信息 -->
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="书名">{{ selectedNovel.title }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selectedNovel.genre }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedNovel.status) }}</el-descriptions-item>
          <el-descriptions-item label="章节数">{{ selectedNovel.total_chapters || 0 }}章</el-descriptions-item>
          <el-descriptions-item label="总字数">{{ selectedNovel.total_words || 0 }}字</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedNovel.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 工具栏 -->
        <div style="margin: 15px 0; display: flex; gap: 10px;">
          <el-button type="success" @click="exportTxt" :loading="exportLoading">
            📥 导出 TXT
          </el-button>
        </div>

        <!-- Tabs 区域 -->
        <el-tabs v-model="viewActiveTab" type="border-card">
          <!-- 章节列表 Tab -->
          <el-tab-pane label="📝 章节列表" name="chapters">
            <el-table :data="chapters" stripe max-height="400">
              <el-table-column prop="chapter_num" label="章节" width="80" />
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="word_count" label="字数" width="80" />
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <el-tag v-if="getChapterRewriteStatus(row.chapter_num) === 'running'" type="warning" effect="dark">
                    重写中...
                  </el-tag>
                  <el-tag v-else-if="getChapterRewriteStatus(row.chapter_num) === 'completed'" type="success" effect="dark">
                    刚完成
                  </el-tag>
                  <el-tag v-else-if="row.status === 'published'" type="success">已发布</el-tag>
                  <el-tag v-else type="info">草稿</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="viewChapter(row)">👁️ 查看</el-button>
                  <el-button size="small" type="warning" @click="rewriteChapter(row)" :disabled="isChapterProcessing(row.chapter_num)">
                    {{ isChapterProcessing(row.chapter_num) ? '⏳ 处理中...' : '🔄 重写' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 蓝图预览 Tab -->
          <el-tab-pane label="📋 蓝图" name="blueprint" :disabled="blueprintLoading">
            <div v-if="blueprintLoading" style="text-align: center; padding: 40px;">
              <el-icon class="is-loading" :size="40"><Loading /></el-icon>
              <p style="margin-top: 15px; color: #666;">加载蓝图中...</p>
            </div>
            <div v-else-if="blueprintData">
              <!-- 蓝图工具栏 -->
              <div style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; justify-content: space-between;">
                <div style="display: flex; gap: 10px;">
                  <el-button type="primary" size="small" @click="openPolishDialog('current')" :disabled="blueprintPolishing">
                    🪄 AI 润色
                  </el-button>
                  <el-button type="warning" size="small" @click="saveBlueprintChanges" :loading="blueprintSaving" :disabled="!blueprintHasChanges">
                    💾 保存修改
                  </el-button>
                </div>
                <el-tag v-if="blueprintHasChanges" type="info" size="small">有未保存的修改</el-tag>
              </div>

              <!-- 蓝图子标签页 -->
              <el-tabs v-model="blueprintActiveTab">
                <el-tab-pane label="🌍 世界观" name="worldMap">
                  <div v-if="blueprintData.world_map" class="blueprint-section">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="世界名称" :span="2">{{ blueprintData.world_map.name || '未命名' }}</el-descriptions-item>
                      <el-descriptions-item label="世界类型">{{ blueprintData.world_map.type || '-' }}</el-descriptions-item>
                      <el-descriptions-item label="力量体系">{{ blueprintData.world_map.power_system || '-' }}</el-descriptions-item>
                    </el-descriptions>
                    <h5 style="margin-top: 15px;">世界概述</h5>
                    <el-input :model-value="blueprintData.world_map.description || '暂无描述'" type="textarea" :rows="4" readonly />
                  </div>
                  <el-empty v-else description="暂无世界观数据" />
                </el-tab-pane>

                <el-tab-pane label="📋 章节规划" name="macroPlot">
                  <div v-if="blueprintData.macro_plot" class="blueprint-section">
                    <el-descriptions :column="3" border size="small">
                      <el-descriptions-item label="总章节数">{{ blueprintData.macro_plot.total_chapters || '-' }}</el-descriptions-item>
                      <el-descriptions-item label="卷数">{{ blueprintData.macro_plot.volumes?.length || '-' }}</el-descriptions-item>
                      <el-descriptions-item label="预计字数">{{ blueprintData.macro_plot.estimated_words || '-' }}</el-descriptions-item>
                    </el-descriptions>
                    <div v-if="blueprintData.macro_plot.volumes?.length" style="margin-top: 15px;">
                      <h5>卷结构</h5>
                      <el-timeline>
                        <el-timeline-item v-for="(volume, idx) in blueprintData.macro_plot.volumes.slice(0, 10)" :key="idx"
                          :timestamp="`第 ${volume.start_chapter || '?'} - ${volume.end_chapter || '?'} 章`" placement="top">
                          <el-card shadow="never" :body-style="{ padding: '10px' }">
                            <h5>{{ volume.name || `第 ${idx + 1} 卷` }}</h5>
                            <p style="font-size: 12px; color: #666;">{{ volume.description || '暂无描述' }}</p>
                          </el-card>
                        </el-timeline-item>
                      </el-timeline>
                    </div>
                  </div>
                  <el-empty v-else description="暂无章节规划数据" />
                </el-tab-pane>

                <el-tab-pane label="👥 人物" name="characters">
                  <div v-if="blueprintData.character_system?.characters?.length" class="blueprint-section">
                    <el-row :gutter="15">
                      <el-col v-for="(char, idx) in blueprintData.character_system.characters.slice(0, 12)" :key="idx" :span="8">
                        <el-card class="character-card" shadow="hover" :body-style="{ padding: '10px' }">
                          <template #header>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                              <span style="font-weight: 600;">{{ char.name || '未命名' }}</span>
                              <el-tag :type="getCharacterType(char.role)" size="small">{{ char.role || '配角' }}</el-tag>
                            </div>
                          </template>
                          <p style="font-size: 12px; color: #666; margin: 0;">{{ (char.description || '暂无描述').substring(0, 100) }}...</p>
                        </el-card>
                      </el-col>
                    </el-row>
                  </div>
                  <el-empty v-else description="暂无人物数据" />
                </el-tab-pane>

                <el-tab-pane label="🎣 伏笔" name="hooks">
                  <div v-if="blueprintData.hook_network?.hooks?.length" class="blueprint-section">
                    <el-table :data="blueprintData.hook_network.hooks.slice(0, 20)" border stripe size="small">
                      <el-table-column prop="name" label="伏笔名称" width="150" />
                      <el-table-column prop="type" label="类型" width="80">
                        <template #default="{ row }">
                          <el-tag :type="getHookType(row.type)" size="small">{{ row.type || '普通' }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="plant_chapter" label="埋设" width="60" />
                      <el-table-column prop="payoff_chapter" label="揭示" width="60" />
                      <el-table-column prop="description" label="描述" show-overflow-tooltip />
                    </el-table>
                  </div>
                  <el-empty v-else description="暂无伏笔数据" />
                </el-tab-pane>
              </el-tabs>
            </div>
            <el-empty v-else description="该小说暂无蓝图数据" />
          </el-tab-pane>

          <!-- 续写 Tab -->
          <el-tab-pane label="✨ 续写" name="continue">
            <div class="continue-section">
              <el-alert title="续写功能说明" type="info" :closable="false" show-icon style="margin-bottom: 20px;">
                <p>续写将根据现有蓝图和已写章节，自动生成下一章内容。</p>
                <p>预计需要 3-5 分钟，生成后章节将自动添加到列表中。</p>
              </el-alert>

              <el-descriptions :column="2" border size="small" style="margin-bottom: 20px;">
                <el-descriptions-item label="当前章节数">{{ selectedNovel.total_chapters || 0 }} 章</el-descriptions-item>
                <el-descriptions-item label="下一章节号">第 {{ (selectedNovel.total_chapters || 0) + 1 }} 章</el-descriptions-item>
                <el-descriptions-item label="蓝图状态">
                  <el-tag v-if="blueprintData" type="success">已有蓝图</el-tag>
                  <el-tag v-else type="warning">暂无蓝图</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="任务状态">
                  <el-tag v-if="continueLoading" type="warning">续写中...</el-tag>
                  <el-tag v-else type="info">等待开始</el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <!-- 续写进度 -->
              <div v-if="continueLoading" class="continue-progress">
                <el-progress :percentage="continueProgress" :format="() => `${continueProgress}%`" :stroke-width="18" striped striped-flow />
                <p style="margin-top: 10px; color: #666;">{{ continueStatus }}</p>
              </div>

              <!-- 续写结果 -->
              <div v-if="continueResult" class="continue-result">
                <el-alert title="续写完成！" type="success" :closable="false" show-icon>
                  <p>第 {{ continueResult.chapter_num }} 章已生成，共 {{ continueResult.word_count }} 字</p>
                </el-alert>
                <el-button type="primary" style="margin-top: 15px;" @click="viewActiveTab = 'chapters'">
                  查看章节列表
                </el-button>
              </div>

              <el-button
                type="primary"
                size="large"
                @click="continueNovel"
                :loading="continueLoading"
                :disabled="!blueprintData"
                style="width: 100%; margin-top: 15px;"
              >
                {{ continueLoading ? '✨ 续写中，请稍候...' : '🚀 开始续写下一章' }}
              </el-button>
              <p v-if="!blueprintData" style="color: #f56c6c; font-size: 12px; margin-top: 10px;">
                ⚠️ 需要先有蓝图才能续写，请先切换到"蓝图"标签页查看或生成蓝图
              </p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
    
    <!-- 章节查看对话框 -->
    <el-dialog v-model="chapterVisible" title="📖 查看章节" width="900px">
      <div v-if="currentChapter">
        <h3>{{ currentChapter.title }}</h3>
        <div class="chapter-content">{{ currentChapter.content || '暂无内容' }}</div>
      </div>
    </el-dialog>

    <!-- 章节重写对话框 -->
    <el-dialog v-model="rewriteVisible" title="🔄 重写章节" width="600px" :close-on-click-modal="!rewriteLoading">
      <div v-if="rewriteChapterData">
        <!-- 重写前提示 -->
        <div v-if="!rewriteLoading">
          <el-alert
            title="重写章节将使用 AI 重新生成该章节内容"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <p>章节：第{{ rewriteChapterData.chapter_num }}章 - {{ rewriteChapterData.title || '无标题' }}</p>
            <p>原字数：{{ rewriteChapterData.word_count || 0 }} 字</p>
          </el-alert>
          <p style="color: #666; font-size: 14px;">
            重写将根据原有大纲重新创作章节内容，保留人物设定和剧情走向。
          </p>
          <el-alert
            title="预计需要 3-5 分钟，请耐心等待"
            type="info"
            :closable="false"
            show-icon
            style="margin-top: 15px;"
          />
        </div>

        <!-- 重写中进度显示 -->
        <div v-else class="rewrite-progress">
          <el-progress
            :percentage="rewriteProgress"
            :format="() => `${rewriteProgress}%`"
            :stroke-width="20"
            striped
            striped-flow
          />
          <div class="progress-steps">
            <p v-for="(step, index) in rewriteSteps" :key="index" :class="{ 'active': index === currentStep, 'done': index < currentStep }">
              <span class="step-icon">{{ index < currentStep ? '✅' : index === currentStep ? '🔄' : '⏳' }}</span>
              {{ step }}
            </p>
          </div>
          <el-alert
            :title="`正在执行：${rewriteSteps[currentStep] || '处理中...'}`"
            type="info"
            :closable="false"
            show-icon
            style="margin-top: 15px;"
          >
            <p>已用时：{{ formatElapsedTime(rewriteStartTime) }}</p>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="rewriteVisible = false" :disabled="rewriteLoading">❌ 取消</el-button>
        <el-button type="primary" @click="confirmRewrite" :loading="rewriteLoading" v-if="!rewriteLoading">
          🔄 确认重写
        </el-button>
      </template>
    </el-dialog>

    <!-- AI 润色对话框 -->
    <el-dialog v-model="blueprintPolishVisible" title="🪄 AI 润色蓝图" width="600px">
      <el-form label-width="100px">
        <el-form-item label="润色范围">
          <el-tag :type="blueprintPolishType === 'all' ? 'success' : 'primary'">
            {{ blueprintPolishType === 'all' ? '全部蓝图' : '仅当前标签页' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="润色要求">
          <el-input
            v-model="blueprintPolishRequirement"
            type="textarea"
            :rows="4"
            placeholder="请输入润色要求，例如：&#10;- 增加更多人物冲突&#10;- 完善世界观细节&#10;- 优化剧情节奏&#10;- 增加伏笔设置"
          />
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon>
          <p>🤖 AI 会自动优化蓝图内容，保持格式不变</p>
          <p>📝 润色后可以继续调整，满意后再保存</p>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="blueprintPolishVisible = false">取消</el-button>
        <el-button type="primary" @click="executeAiPolish" :loading="blueprintPolishing">
          🚀 开始润色
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="✏️ 编辑小说" width="600px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="书名" required>
          <el-input v-model="editForm.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="editForm.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="玄幻" value="玄幻" />
            <el-option label="仙侠" value="仙侠" />
            <el-option label="都市" value="都市" />
            <el-option label="历史" value="历史" />
            <el-option label="科幻" value="科幻" />
            <el-option label="游戏" value="游戏" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.description" type="textarea" :rows="4" placeholder="小说简介" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="editForm.status" placeholder="选择状态" style="width: 100%">
            <el-option label="连载中" value="ongoing" />
            <el-option label="已完成" value="completed" />
            <el-option label="暂停" value="paused" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">❌ 取消</el-button>
        <el-button type="primary" @click="confirmEdit">💾 保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 下载对话框 -->
    <el-dialog v-model="downloadVisible" title="📥 下载小说" width="500px">
      <el-form label-width="100px">
        <el-form-item label="下载格式" required>
          <el-radio-group v-model="downloadFormat">
            <el-radio label="txt">📄 TXT 文本</el-radio>
            <el-radio label="md">📝 Markdown</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="downloadVisible = false">❌ 取消</el-button>
        <el-button type="primary" @click="confirmDownload">⬇️ 下载</el-button>
      </template>
    </el-dialog>
    
    <!-- 批量下载对话框 -->
    <el-dialog v-model="batchDownloadVisible" title="📥 批量下载" width="500px">
      <el-form label-width="100px">
        <el-form-item label="下载格式" required>
          <el-radio-group v-model="downloadFormat">
            <el-radio label="txt">📄 TXT 文本</el-radio>
            <el-radio label="md">📝 Markdown</el-radio>
            <el-radio label="zip">📦 ZIP 压缩包</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-alert
          title="批量下载提示"
          type="info"
          :closable="false"
          show-icon
        >
          <p>将下载 {{ selectedNovels.length }} 本小说：</p>
          <ul>
            <li v-for="id in selectedNovels" :key="id">
              {{ novels.find(n => n.id === id)?.title }}
            </li>
          </ul>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="batchDownloadVisible = false">❌ 取消</el-button>
        <el-button type="primary" @click="confirmBatchDownload">⬇️ 开始下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiClient } from '@/api/client'
import NovelCard from '@/components/NovelCard.vue'
import BlueprintViewer from '@/components/BlueprintViewer.vue'

const router = useRouter()

// 搜索和筛选
const searchQuery = ref('')
const filterGenre = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(9)

// 数据
const novels = ref([])
const chapters = ref([])

// 批量选择
const selectedNovels = ref([])

// 对话框
const viewVisible = ref(false)
const editVisible = ref(false)
const chapterVisible = ref(false)
const downloadVisible = ref(false)
const batchDownloadVisible = ref(false)

// 当前选中
const selectedNovel = ref(null)
const currentChapter = ref(null)
const downloadNovelId = ref('')

// 编辑表单
const editForm = reactive({
  title: '',
  genre: '',
  description: '',
  status: 'ongoing'
})

// 下载选项
const downloadFormat = ref('txt')

// 计算属性
const filteredNovels = computed(() => {
  return novels.value.filter(novel => {
    const matchSearch = !searchQuery.value || novel.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchGenre = !filterGenre.value || novel.genre === filterGenre.value
    const matchStatus = !filterStatus.value || novel.status === filterStatus.value
    return matchSearch && matchGenre && matchStatus
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredNovels.value.length / pageSize.value)
})

const paginatedNovels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredNovels.value.slice(start, end)
})

// 方法
const loadNovels = async () => {
  try {
    const result = await apiClient.novels.list()
    if (result.data && result.data.novels) {
      novels.value = result.data.novels
      currentPage.value = 1
      ElMessage.success(`加载了 ${novels.value.length} 本小说`)
    }
  } catch (error) {
    ElMessage.error('加载小说列表失败：' + error.message)
  }
}

const viewNovel = async (novelId) => {
  try {
    const result = await apiClient.novels.get(novelId)
    selectedNovel.value = result.data
    const chaptersResult = await apiClient.novels.getChapters(novelId)
    chapters.value = chaptersResult.data?.chapters || []

    // 重置标签页状态
    viewActiveTab.value = 'chapters'
    continueResult.value = null
    continueProgress.value = 0
    continueStatus.value = ''

    // 预加载蓝图数据
    blueprintLoading.value = true
    blueprintData.value = null
    try {
      const bpResult = await apiClient.novels.getBlueprint(novelId)
      if (bpResult.data?.blueprint) {
        blueprintData.value = bpResult.data.blueprint
      }
    } catch (e) {
      console.log('蓝图加载失败或不存在')
    } finally {
      blueprintLoading.value = false
    }

    viewVisible.value = true
  } catch (error) {
    ElMessage.error('加载小说详情失败：' + error.message)
  }
}

const viewChapter = (chapter) => {
  currentChapter.value = chapter
  chapterVisible.value = true
}

// 重写章节相关
const rewriteVisible = ref(false)
const rewriteChapterData = ref(null)
const rewriteLoading = ref(false)
const rewriteProgress = ref(0)
const rewriteStartTime = ref(null)
const currentStep = ref(0)
const rewriteSteps = [
  '剧情架构师 - 细化大纲',
  '人物设计师 - 准备角色',
  '章节写手 - 撰写初稿',
  '对话专家 - 打磨对话',
  '审核编辑 - 质量把控',
  '主编 - 最终审核'
]

// 续写相关
const continueLoading = ref(false)
const blueprintLoading = ref(false)
const exportLoading = ref(false)
const blueprintVisible = ref(false)
const blueprintData = ref(null)
const blueprintActiveTab = ref('world_map')
const viewActiveTab = ref('chapters')
const continueProgress = ref(0)
const continueStatus = ref('')
const continueResult = ref(null)

// AI 润色相关
const blueprintPolishing = ref(false)
const blueprintPolishVisible = ref(false)
const blueprintPolishType = ref('current')
const blueprintPolishRequirement = ref('')
const blueprintHasChanges = ref(false)
const blueprintSaving = ref(false)

// 标记蓝图有修改
const markBlueprintChanged = () => {
  blueprintHasChanges.value = true
}

// 保存蓝图修改
const saveBlueprintChanges = async () => {
  if (!blueprintData.value || !selectedNovel.value) return

  blueprintSaving.value = true
  try {
    const result = await apiClient.novels.updateBlueprint(selectedNovel.value.id, {
      world_map: blueprintData.value.world_map,
      macro_plot: blueprintData.value.macro_plot,
      character_system: blueprintData.value.character_system,
      hook_network: blueprintData.value.hook_network
    })

    if (result.success) {
      blueprintHasChanges.value = false
      ElMessage.success('蓝图修改已保存！')
    } else {
      ElMessage.error('保存失败：' + (result.error || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    blueprintSaving.value = false
  }
}

// 追踪运行中的重写任务 { chapter_num: { taskId, status } }
const runningRewriteTasks = ref({})

// 获取章节重写状态
const getChapterRewriteStatus = (chapterNum) => {
  const task = runningRewriteTasks.value[chapterNum]
  return task?.status || null
}

// 检查章节是否正在处理中（包括排队中）
const isChapterProcessing = (chapterNum) => {
  const status = getChapterRewriteStatus(chapterNum)
  return status === 'running' || status === 'queued'
}

// 格式化已用时间
const formatElapsedTime = (startTime) => {
  if (!startTime) return '0秒'
  const elapsed = Math.floor((Date.now() - startTime) / 1000)
  const minutes = Math.floor(elapsed / 60)
  const seconds = elapsed % 60
  if (minutes > 0) {
    return `${minutes}分${seconds}秒`
  }
  return `${seconds}秒`
}

const rewriteChapter = (chapter) => {
  rewriteChapterData.value = chapter
  rewriteVisible.value = true
}

const confirmRewrite = async () => {
  if (!rewriteChapterData.value) return

  // 检查该章节是否已有任务在处理中
  if (isChapterProcessing(rewriteChapterData.value.chapter_num)) {
    ElMessage.warning('该章节已有重写任务在处理中，请等待完成')
    return
  }

  rewriteLoading.value = true

  try {
    // 创建重写任务
    const createResult = await apiClient.novels.rewriteChapter(
      selectedNovel.value.id,
      rewriteChapterData.value.chapter_num
    )

    const taskId = createResult.data?.task_id
    if (!taskId) {
      ElMessage.error('创建重写任务失败')
      rewriteLoading.value = false
      return
    }

    // 任务已创建，关闭对话框
    rewriteVisible.value = false
    rewriteLoading.value = false

    // 显示任务 ID，提示用户稍后刷新查看
    ElMessage.success({
      message: `重写任务已创建！任务ID: ${taskId.slice(-8)}，请稍后刷新查看结果`,
      duration: 5000
    })

    // 启动后台轮询，完成后自动刷新
    startBackgroundPoll(taskId, rewriteChapterData.value.chapter_num)

  } catch (error) {
    ElMessage.error('重写失败：' + error.message)
    rewriteLoading.value = false
  }
}

// 后台轮询任务状态
const startBackgroundPoll = (taskId, chapterNum) => {
  // 标记为运行中
  runningRewriteTasks.value[chapterNum] = { taskId, status: 'queued' }

  const pollInterval = setInterval(async () => {
    try {
      const statusResult = await apiClient.novels.getTask(taskId)
      const task = statusResult.data

      if (task?.status === 'completed') {
        clearInterval(pollInterval)
        runningRewriteTasks.value[chapterNum] = { taskId, status: 'completed' }
        ElMessage.success(`第${task.chapter_num}章重写完成！共 ${task.result?.word_count || 0} 字`)
        // 自动刷新章节列表
        if (selectedNovel.value) {
          await viewNovel(selectedNovel.value.id)
        }
        // 5秒后清除完成标记
        setTimeout(() => {
          delete runningRewriteTasks.value[chapterNum]
        }, 5000)
      } else if (task?.status === 'failed') {
        clearInterval(pollInterval)
        delete runningRewriteTasks.value[chapterNum]
        ElMessage.error(`重写失败：${task.error || '未知错误'}`)
      } else if (task?.status === 'queued') {
        // 更新队列状态
        runningRewriteTasks.value[chapterNum] = {
          taskId,
          status: 'queued',
          queuePosition: task.queue_position || 0
        }
      } else if (task?.status === 'running') {
        runningRewriteTasks.value[chapterNum] = { taskId, status: 'running' }
      }
    } catch (pollError) {
      console.error('轮询状态失败:', pollError)
    }
  }, 3000) // 每 3 秒轮询一次
}

const editNovel = async (novelId) => {
  try {
    const result = await apiClient.novels.get(novelId)
    const novel = result.data
    
    editForm.title = novel.title
    editForm.genre = novel.genre || '玄幻'
    editForm.description = novel.description || ''
    editForm.status = novel.status || 'ongoing'
    selectedNovel.value = novel
    
    editVisible.value = true
  } catch (error) {
    ElMessage.error('加载小说信息失败：' + error.message)
  }
}

const confirmEdit = async () => {
  try {
    await apiClient.novels.update(selectedNovel.value.id, {
      title: editForm.title,
      genre: editForm.genre,
      description: editForm.description,
      status: editForm.status
    })
    
    ElMessage.success('小说信息已更新')
    editVisible.value = false
    loadNovels()
  } catch (error) {
    ElMessage.error('更新失败：' + error.message)
  }
}

const continueWriting = (novelId) => {
  localStorage.setItem('writing_panel_state', JSON.stringify({ selectedNovelId: novelId }))
  router.push('/writing')
}

// 续写小说
const continueNovel = async () => {
  if (!selectedNovel.value) return

  continueLoading.value = true
  continueProgress.value = 0
  continueStatus.value = '正在创建续写任务...'
  continueResult.value = null

  try {
    const result = await apiClient.novels.continueNovel(selectedNovel.value.id)

    if (result.data?.task_id) {
      const taskId = result.data.task_id
      const chapterNum = result.data.chapter_num
      const queuePosition = result.data.queue_position || 0

      continueStatus.value = `任务已加入队列（位置 ${queuePosition}），正在生成第 ${chapterNum} 章...`
      continueProgress.value = 10

      // 轮询任务状态
      const pollInterval = setInterval(async () => {
        try {
          const statusResult = await apiClient.novels.getTask(taskId)
          const task = statusResult.data

          if (task?.status === 'completed') {
            clearInterval(pollInterval)
            continueProgress.value = 100
            continueStatus.value = '续写完成！'
            continueResult.value = {
              chapter_num: task.chapter_num,
              word_count: task.result?.word_count || 0
            }
            ElMessage.success(`第${task.chapter_num}章续写完成！共 ${task.result?.word_count || 0} 字`)
            // 刷新章节列表
            const chaptersResult = await apiClient.novels.getChapters(selectedNovel.value.id)
            chapters.value = chaptersResult.data?.chapters || []
            // 更新小说信息
            selectedNovel.value.total_chapters = chapters.value.length
            continueLoading.value = false
          } else if (task?.status === 'failed') {
            clearInterval(pollInterval)
            continueStatus.value = '续写失败'
            ElMessage.error(`续写失败：${task.error || '未知错误'}`)
            continueLoading.value = false
          } else if (task?.status === 'queued') {
            continueStatus.value = `任务排队中，前面还有 ${task.queue_position || 0} 个任务`
            continueProgress.value = 15
          } else if (task?.status === 'running') {
            continueProgress.value = Math.min(90, 30 + (task.progress || 0) * 0.6)
            continueStatus.value = task.current_step || '正在创作中...'
          }
        } catch (pollError) {
          console.error('轮询续写状态失败:', pollError)
        }
      }, 3000)
    } else {
      ElMessage.error('创建续写任务失败')
      continueLoading.value = false
    }
  } catch (error) {
    continueStatus.value = '续写失败'
    ElMessage.error('续写失败：' + (error.response?.data?.detail || error.message))
    continueLoading.value = false
  }
}

// 查看蓝图（切换到蓝图标签页）
const viewBlueprint = async () => {
  if (!selectedNovel.value) return

  // 如果还没有加载蓝图数据，先加载
  if (!blueprintData.value) {
    blueprintLoading.value = true
    blueprintHasChanges.value = false
    try {
      const result = await apiClient.novels.getBlueprint(selectedNovel.value.id)
      if (result.data?.blueprint) {
        blueprintData.value = result.data.blueprint
      } else {
        ElMessage.warning('该小说暂无蓝图数据')
        return
      }
    } catch (error) {
      ElMessage.error('获取蓝图失败：' + error.message)
      return
    } finally {
      blueprintLoading.value = false
    }
  }

  // 切换到蓝图标签页
  viewActiveTab.value = 'blueprint'
}

// 导出 TXT
const exportTxt = async () => {
  if (!selectedNovel.value) return

  exportLoading.value = true
  try {
    // 直接下载文件 - 使用正确的 API 路径
    const response = await fetch(`/api/novels/${selectedNovel.value.id}/export/txt`)
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error?.message || '导出失败')
    }

    // 获取文件名（处理 UTF-8 编码的文件名）
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `${selectedNovel.value.title}.txt`
    if (contentDisposition) {
      // 尝试解析 filename*=UTF-8'' 格式
      const utf8Match = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (utf8Match) {
        filename = decodeURIComponent(utf8Match[1])
      } else {
        // 尝试解析普通 filename 格式
        const match = contentDisposition.match(/filename="(.+)"/)
        if (match) filename = match[1]
      }
    }

    // 下载文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    ElMessage.success(`《${selectedNovel.value.title}》已导出为 TXT`)
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  } finally {
    exportLoading.value = false
  }
}

// ========== 蓝图编辑功能 ==========

const startEditBlueprint = () => {
  if (!blueprintData.value) return

  // 初始化编辑数据
  blueprintEditData.value = {
    world_map_text: JSON.stringify(blueprintData.value.world_map || {}, null, 2),
    macro_plot_text: JSON.stringify(blueprintData.value.macro_plot || {}, null, 2),
    character_system_text: JSON.stringify(blueprintData.value.character_system || {}, null, 2),
    hook_network_text: JSON.stringify(blueprintData.value.hook_network || {}, null, 2)
  }
  blueprintEditing.value = true
  ElMessage.success('已进入编辑模式，可以直接修改蓝图内容')
}

const cancelEditBlueprint = () => {
  blueprintEditing.value = false
  blueprintEditData.value = {
    world_map_text: '',
    macro_plot_text: '',
    character_system_text: '',
    hook_network_text: ''
  }
  ElMessage.info('已取消编辑')
}

const saveBlueprint = async () => {
  if (!selectedNovel.value) return

  blueprintSaving.value = true
  try {
    // 解析 JSON 并验证
    const worldMap = safeParseJson(blueprintEditData.value.world_map_text, {})
    const macroPlot = safeParseJson(blueprintEditData.value.macro_plot_text, {})
    const characterSystem = safeParseJson(blueprintEditData.value.character_system_text, {})
    const hookNetwork = safeParseJson(blueprintEditData.value.hook_network_text, {})

    // 调用 API 保存
    await apiClient.novels.update(selectedNovel.value.id, {
      settings: {
        world_map: worldMap,
        macro_plot: macroPlot,
        character_system: characterSystem,
        hook_network: hookNetwork
      }
    })

    // 更新本地数据
    blueprintData.value = {
      world_map: worldMap,
      macro_plot: macroPlot,
      character_system: characterSystem,
      hook_network: hookNetwork
    }

    blueprintEditing.value = false
    ElMessage.success('蓝图已保存！')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    blueprintSaving.value = false
  }
}

const safeParseJson = (text, defaultValue) => {
  try {
    return JSON.parse(text)
  } catch {
    ElMessage.warning('JSON 格式不正确，将使用默认值')
    return defaultValue
  }
}

const aiPolishBlueprint = () => {
  blueprintPolishType.value = 'current'
  blueprintPolishRequirement.value = ''
  blueprintPolishVisible.value = true
}

const executeAiPolish = async () => {
  if (!blueprintPolishRequirement.value.trim()) {
    ElMessage.warning('请输入润色要求')
    return
  }

  blueprintPolishing.value = true
  blueprintPolishVisible.value = false

  try {
    // 获取当前要润色的内容
    let contentToPolish = ''
    let fieldName = ''

    if (blueprintPolishType.value === 'current') {
      fieldName = blueprintActiveTab.value
      contentToPolish = JSON.stringify(blueprintData.value[fieldName] || {}, null, 2)
    } else {
      // 全部润色
      contentToPolish = JSON.stringify({
        world_map: blueprintData.value.world_map || {},
        macro_plot: blueprintData.value.macro_plot || {},
        character_system: blueprintData.value.character_system || {},
        hook_network: blueprintData.value.hook_network || {}
      }, null, 2)
    }

    // 调用 AI 润色 API
    const result = await apiClient.novels.polishBlueprint(
      selectedNovel.value.id,
      {
        type: blueprintPolishType.value,
        field: blueprintActiveTab.value,
        content: contentToPolish,
        requirement: blueprintPolishRequirement.value
      }
    )

    if (result.data?.polished_content) {
      // 解析润色结果
      const polished = safeParseJson(result.data.polished_content, {})

      if (blueprintPolishType.value === 'current' && polished) {
        // 更新当前标签页
        blueprintData.value[fieldName] = polished
      } else if (blueprintPolishType.value === 'all') {
        // 更新全部
        if (polished.world_map) blueprintData.value.world_map = polished.world_map
        if (polished.macro_plot) blueprintData.value.macro_plot = polished.macro_plot
        if (polished.character_system) blueprintData.value.character_system = polished.character_system
        if (polished.hook_network) blueprintData.value.hook_network = polished.hook_network
      }

      // 标记有修改
      blueprintHasChanges.value = true
      ElMessage.success('AI 润色完成！点击"保存修改"按钮保存')
    } else {
      ElMessage.error('润色失败，请重试')
    }
  } catch (error) {
    ElMessage.error('润色失败：' + error.message)
  } finally {
    blueprintPolishing.value = false
  }
}

const startDownload = (novelId) => {
  downloadNovelId.value = novelId
  downloadVisible.value = true
}

const confirmDownload = async () => {
  try {
    const novelId = downloadNovelId.value
    const chaptersResult = await apiClient.novels.getChapters(novelId)
    const allChapters = chaptersResult.data?.chapters || []
    
    if (allChapters.length === 0) {
      ElMessage.warning('暂无章节可下载')
      return
    }
    
    const novel = novels.value.find(n => n.id === novelId)
    
    if (downloadFormat.value === 'txt') {
      const content = allChapters.map(ch => `第${ch.chapter_num}章 ${ch.title || ''}\n\n${ch.content || ''}\n\n`).join('---\n\n')
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${novel?.title || '小说'}.txt`
      a.click()
      URL.revokeObjectURL(url)
    } else if (downloadFormat.value === 'md') {
      const content = `# ${novel?.title || '小说'}\n\n**类型**: ${novel?.genre || ''}\n**简介**: ${novel?.description || ''}\n\n---\n\n` +
        allChapters.map(ch => `## 第${ch.chapter_num}章 ${ch.title || ''}\n\n${ch.content || ''}\n\n`).join('---\n\n')
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${novel?.title || '小说'}.md`
      a.click()
      URL.revokeObjectURL(url)
    }
    
    downloadVisible.value = false
    ElMessage.success(`下载成功！格式：${downloadFormat.value.toUpperCase()}`)
  } catch (error) {
    ElMessage.error('下载失败：' + error.message)
  }
}

const deleteNovel = async (novelId) => {
  try {
    await ElMessageBox.confirm('确定要删除这本小说吗？删除后可在回收站恢复。', '确认删除', {
      confirmButtonText: '移到回收站',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await apiClient.novels.delete(novelId)
    ElMessage.success('小说已移至回收站')
    loadNovels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

const batchDownload = () => {
  if (selectedNovels.value.length === 0) {
    ElMessage.warning('请先选择要下载的小说')
    return
  }
  batchDownloadVisible.value = true
}

const confirmBatchDownload = async () => {
  try {
    for (const novelId of selectedNovels.value) {
      const novel = novels.value.find(n => n.id === novelId)
      if (!novel) continue
      
      const chaptersResult = await apiClient.novels.getChapters(novelId)
      const allChapters = chaptersResult.data?.chapters || []
      
      if (allChapters.length === 0) continue
      
      if (downloadFormat.value === 'txt') {
        const content = allChapters.map(ch => `第${ch.chapter_num}章 ${ch.title || ''}\n\n${ch.content || ''}\n\n`).join('---\n\n')
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${novel.title}.txt`
        a.click()
        URL.revokeObjectURL(url)
      } else if (downloadFormat.value === 'md') {
        const content = `# ${novel.title}\n\n**类型**: ${novel.genre}\n**简介**: ${novel.description}\n\n---\n\n` +
          allChapters.map(ch => `## 第${ch.chapter_num}章 ${ch.title || ''}\n\n${ch.content || ''}\n\n`).join('---\n\n')
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${novel.title}.md`
        a.click()
        URL.revokeObjectURL(url)
      }
    }
    
    batchDownloadVisible.value = false
    ElMessage.success(`批量下载成功！共下载 ${selectedNovels.value.length} 本小说`)
    clearSelection()
  } catch (error) {
    ElMessage.error('批量下载失败：' + error.message)
  }
}

const batchDelete = async () => {
  if (selectedNovels.value.length === 0) {
    ElMessage.warning('请先选择要删除的小说')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedNovels.value.length} 本小说吗？删除后可在回收站恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '移到回收站',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    for (const novelId of selectedNovels.value) {
      try {
        await apiClient.novels.delete(novelId)
      } catch (error) {
        console.error(`删除小说 ${novelId} 失败:`, error)
      }
    }
    
    ElMessage.success(`已将 ${selectedNovels.value.length} 本小说移至回收站`)
    clearSelection()
    loadNovels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败：' + error.message)
    }
  }
}

const clearSelection = () => {
  selectedNovels.value = []
}

// 格式化日期 - 修复时区问题
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

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'ongoing': '连载中',
    'completed': '已完成',
    'paused': '暂停',
    'deleted': '已删除'
  }
  return statusMap[status] || status || '未知'
}

// 获取人物类型标签样式
const getCharacterType = (role) => {
  const typeMap = {
    '主角': 'danger',
    '女主': 'warning',
    '反派': 'info',
    '配角': 'success'
  }
  return typeMap[role] || ''
}

// 获取伏笔类型标签样式
const getHookType = (type) => {
  const typeMap = {
    '短篇': '',
    '中篇': 'warning',
    '长篇': 'success',
    '终极': 'danger'
  }
  return typeMap[type] || ''
}

onMounted(() => {
  loadNovels()
})
</script>

<style scoped>
.novel-library { max-width: 1400px; margin: 0 auto; padding: 20px; }
.batch-card { margin-bottom: 20px; background: #fff7e6; border-color: #ffd591; }
.batch-toolbar { display: flex; justify-content: space-between; align-items: center; }
.batch-info { font-size: 14px; color: #d46b08; font-weight: bold; }
.batch-actions { display: flex; gap: 10px; }
.filter-card { margin-bottom: 20px; }
.chapter-content { max-height: 500px; overflow-y: auto; padding: 20px; background: #f9f9f9; border-radius: 4px; line-height: 2; font-size: 15px; white-space: pre-wrap; }
.rewrite-progress { padding: 10px 0; }
.progress-steps { margin-top: 20px; }
.progress-steps p { margin: 8px 0; font-size: 14px; color: #909399; transition: all 0.3s; }
.progress-steps p.active { color: #409EFF; font-weight: bold; }
.progress-steps p.done { color: #67C23A; }
.step-icon { margin-right: 8px; }
.continue-section { padding: 20px 0; }
.continue-progress { padding: 20px 0; text-align: center; }
.continue-result { padding: 20px 0; text-align: center; }
.blueprint-section { padding: 10px 0; }
.blueprint-section h5 { margin: 15px 0 10px; color: #606266; }
.character-card { margin-bottom: 15px; }
.character-card :deep(.el-card__header) { padding: 10px 15px; }
</style>
