<template>
  <div class="learning-panel">
    <h2>📚 学习中心</h2>

    <el-row :gutter="20">
      <!-- 上传作品分析 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>上传作品分析</span>
              <el-button type="primary" @click="analyzeWork" :loading="analyzing">
                {{ analyzing ? '分析中...' : '开始分析' }}
              </el-button>
            </div>
          </template>

          <!-- Tab 切换 -->
          <el-tabs v-model="uploadTab" class="upload-tabs">
            <!-- Tab 1: 文字粘贴 -->
            <el-tab-pane label="📝 文字粘贴" name="text">
              <el-form label-width="80px">
                <el-form-item label="作者">
                  <el-input v-model="uploadForm.author" placeholder="例如：金庸" />
                </el-form-item>

                <el-form-item label="作品名">
                  <el-input v-model="uploadForm.title" placeholder="例如：天龙八部" />
                </el-form-item>

                <el-form-item label="小说内容">
                  <el-input
                    v-model="uploadForm.text"
                    type="textarea"
                    :rows="15"
                    placeholder="粘贴小说内容，支持长文本（系统会自动分块处理）"
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- Tab 2: 文件/URL 上传 -->
            <el-tab-pane label="📁 文件/链接" name="file">
              <el-form label-width="80px">
                <el-form-item label="作者">
                  <el-input v-model="fileForm.author" placeholder="例如：金庸" />
                </el-form-item>

                <el-form-item label="作品名">
                  <el-input v-model="fileForm.title" placeholder="例如：天龙八部" />
                </el-form-item>

                <!-- 文件上传区域 -->
                <el-form-item label="上传文件">
                  <el-upload
                    ref="uploadRef"
                    class="upload-area"
                    drag
                    multiple
                    :auto-upload="false"
                    :file-list="fileList"
                    :on-change="handleFileChange"
                    :on-remove="handleFileRemove"
                    accept=".txt,.md,.pdf,.doc,.docx"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      拖拽文件到此处，或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 txt、md、pdf、doc、docx 格式，支持批量上传
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>

                <!-- 已选文件列表 -->
                <el-form-item v-if="selectedFiles.length > 0" label="已选文件">
                  <div class="file-list">
                    <el-tag
                      v-for="(file, index) in selectedFiles"
                      :key="index"
                      closable
                      @close="removeFile(index)"
                      style="margin: 4px"
                    >
                      {{ file.name }} ({{ formatFileSize(file.size) }})
                    </el-tag>
                    <el-button
                      size="small"
                      type="primary"
                      @click="convertAllFiles"
                      :loading="converting"
                      style="margin-left: 8px"
                    >
                      转换全部
                    </el-button>
                  </div>
                </el-form-item>

                <el-divider>或者输入网页链接</el-divider>

                <!-- URL 输入 -->
                <el-form-item label="网页链接">
                  <el-input
                    v-model="fileForm.url"
                    placeholder="输入网页 URL 或在线文档链接"
                    clearable
                  >
                    <template #append>
                      <el-button @click="fetchUrl" :loading="urlFetching">
                        获取
                      </el-button>
                    </template>
                  </el-input>
                </el-form-item>

                <!-- 转换结果预览 -->
                <el-form-item v-if="convertedText" label="内容预览">
                  <div class="converted-preview">
                    <div class="preview-header">
                      <span>共 {{ convertedText.length }} 字符，{{ segmentCount }} 段</span>
                      <el-button size="small" @click="clearConverted">清除</el-button>
                    </div>
                    <el-input
                      :model-value="convertedText.substring(0, 500) + (convertedText.length > 500 ? '...' : '')"
                      type="textarea"
                      :rows="6"
                      readonly
                    />
                  </div>
                </el-form-item>

                <!-- 转换状态 -->
                <el-form-item v-if="convertingStatus">
                  <el-alert
                    :title="convertingStatus"
                    :type="convertingError ? 'error' : 'info'"
                    :closable="false"
                    show-icon
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <!-- 分析说明（两个 tab 共用） -->
          <el-alert
            title="分析说明"
            type="info"
            :closable="false"
            show-icon
            style="margin-top: 16px"
          >
            <p>系统会自动分析作品的：</p>
            <ul>
              <li>叙事风格（视角、节奏、结构）</li>
              <li>描写风格（密度、手法、感官）</li>
              <li>对话风格（比例、特点、潜台词）</li>
              <li>情感风格（强度、表达方式）</li>
            </ul>
            <p>并提取可复用的写作模式和技巧。</p>
          </el-alert>
        </el-card>
      </el-col>
      
      <!-- 已分析作品列表 -->
      <el-col :span="12">
        <el-card>
          <template #header>已分析作品</template>
          
          <el-table :data="analyzedWorks" style="width: 100%">
            <el-table-column prop="author" label="作者" width="80" />
            <el-table-column prop="title" label="作品" />
            <el-table-column prop="analyzed_at" label="分析时间" width="160" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="viewWorkDetail(row)">详情</el-button>
                <el-button size="small" type="primary" @click="applyStyle(row)">应用</el-button>
                <el-popconfirm
                  title="确定删除此分析？"
                  confirm-button-text="删除"
                  cancel-button-text="取消"
                  @confirm="deleteWork(row)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        
        <!-- 学习报告 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>学习报告</span>
              <el-button @click="generateReport" :loading="reportLoading">刷新</el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="已分析作品">
              {{ report.analyzed_works }} 部
            </el-descriptions-item>
            <el-descriptions-item label="学习到的特征">
              {{ report.style_features_learned }} 个
            </el-descriptions-item>
            <el-descriptions-item label="已评估章节">
              {{ report.chapters_evaluated }} 章
            </el-descriptions-item>
            <el-descriptions-item label="平均评分">
              {{ report.average_score }}/10
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <h4>改进建议</h4>
          <ul>
            <li v-for="(rec, index) in report.recommendations" :key="index">
              {{ rec }}
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 作品详情对话框 -->
    <el-dialog v-model="detailVisible" title="作品分析详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="作者">{{ selectedWork.author }}</el-descriptions-item>
        <el-descriptions-item label="作品">{{ selectedWork.title }}</el-descriptions-item>
        <el-descriptions-item label="分析时间" :span="2">
          {{ selectedWork.analyzed_at }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>叙事风格</el-divider>
      <el-tag v-for="feature in selectedWork.analysis?.narrative_style" :key="feature">
        {{ feature }}
      </el-tag>
      
      <el-divider>描写风格</el-divider>
      <el-tag v-for="feature in selectedWork.analysis?.description_style" :key="feature">
        {{ feature }}
      </el-tag>
      
      <el-divider>对话风格</el-divider>
      <el-tag v-for="feature in selectedWork.analysis?.dialogue_style" :key="feature">
        {{ feature }}
      </el-tag>
      
      <el-divider>情感风格</el-divider>
      <el-tag v-for="feature in selectedWork.analysis?.emotional_style" :key="feature">
        {{ feature }}
      </el-tag>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="applyStyle(selectedWork)">应用此风格</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { apiClient } from '@/api/client'

const analyzing = ref(false)
const reportLoading = ref(false)
const detailVisible = ref(false)

// Tab 切换
const uploadTab = ref('text')

// 文字粘贴表单
const uploadForm = reactive({
  author: '',
  title: '',
  text: ''
})

// 文件/URL 表单
const fileForm = reactive({
  author: '',
  title: '',
  url: ''
})

// 文件上传相关
const uploadRef = ref()
const fileList = ref([])
const selectedFiles = ref([])
const convertedText = ref('')
const segmentCount = ref(0)
const convertingStatus = ref('')
const convertingError = ref(false)
const converting = ref(false)
const urlFetching = ref(false)

const analyzedWorks = ref([])

const selectedWork = ref({})

const report = reactive({
  analyzed_works: 0,
  style_features_learned: 0,
  chapters_evaluated: 0,
  average_score: 0,
  recommendations: []
})

// 文件选择处理
const handleFileChange = (uploadFile, uploadFiles) => {
  // 添加到已选文件列表
  const exists = selectedFiles.value.some(f => f.name === uploadFile.name)
  if (!exists && uploadFile.raw) {
    selectedFiles.value.push({
      name: uploadFile.name,
      size: uploadFile.size,
      raw: uploadFile.raw,
      status: 'pending'
    })
  }
}

// 移除单个文件
const handleFileRemove = (uploadFile) => {
  const index = selectedFiles.value.findIndex(f => f.name === uploadFile.name)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  }
}

// 手动移除文件
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  // 同步更新 upload 组件的文件列表
  if (uploadRef.value) {
    const file = selectedFiles.value[index]
    uploadRef.value.handleRemove(file)
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 批量转换所有文件
const convertAllFiles = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  converting.value = true
  convertingError.value = false
  convertingStatus.value = `正在转换 ${selectedFiles.value.length} 个文件...`

  const allSegments = []
  let successCount = 0
  let failCount = 0

  for (const file of selectedFiles.value) {
    file.status = 'converting'
    convertingStatus.value = `正在转换: ${file.name}`

    try {
      const formData = new FormData()
      formData.append('file', file.raw)

      const response = await fetch('/api/learning/convert/file', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (result.status === 'success') {
        allSegments.push(...result.data.segments)
        file.status = 'success'
        successCount++
      } else {
        throw new Error(result.message || '转换失败')
      }
    } catch (error) {
      file.status = 'error'
      failCount++
      console.error(`文件 ${file.name} 转换失败:`, error)
    }
  }

  // 合并所有内容
  if (allSegments.length > 0) {
    convertedText.value = allSegments.join('\n\n')
    segmentCount.value = allSegments.length
  }

  // 显示结果
  if (failCount === 0) {
    convertingStatus.value = `✅ 全部转换成功！共 ${successCount} 个文件，${convertedText.value.length} 字符`
    ElMessage.success(`成功转换 ${successCount} 个文件`)
  } else {
    convertingError.value = true
    convertingStatus.value = `⚠️ 转换完成：${successCount} 成功，${failCount} 失败`
    ElMessage.warning(`${successCount} 个文件转换成功，${failCount} 个失败`)
  }

  converting.value = false
}

// URL 获取
const fetchUrl = async () => {
  if (!fileForm.url) {
    ElMessage.warning('请输入网页链接')
    return
  }

  urlFetching.value = true
  convertingStatus.value = '正在获取网页内容...'
  convertingError.value = false

  try {
    const formData = new FormData()
    formData.append('url', fileForm.url)

    const response = await fetch('/api/learning/convert/url', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.status === 'success') {
      convertedText.value = result.data.segments.join('\n\n')
      segmentCount.value = result.data.segment_count
      convertingStatus.value = `✅ ${result.message}`
      ElMessage.success(result.message)
    } else {
      throw new Error(result.message || '获取失败')
    }
  } catch (error) {
    convertingError.value = true
    convertingStatus.value = `❌ 获取失败：${error.message}`
    ElMessage.error('网页获取失败：' + error.message)
  } finally {
    urlFetching.value = false
  }
}

// 清除转换结果
const clearConverted = () => {
  convertedText.value = ''
  segmentCount.value = 0
  convertingStatus.value = ''
  selectedFiles.value = []
  fileForm.url = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const analyzeWork = async () => {
  // 根据当前 tab 获取内容
  let author, title, text

  if (uploadTab.value === 'text') {
    author = uploadForm.author
    title = uploadForm.title
    text = uploadForm.text

    if (!author || !title || !text) {
      ElMessage.warning('请填写作者、作品名和小说内容')
      return
    }
  } else {
    author = fileForm.author
    title = fileForm.title

    if (!author || !title) {
      ElMessage.warning('请填写作者和作品名')
      return
    }

    // 如果有未转换的文件，先自动转换
    if (selectedFiles.value.length > 0 && !convertedText.value) {
      await convertAllFiles()
    }

    text = convertedText.value

    if (!text) {
      ElMessage.warning('请上传文件或输入网页链接，并点击转换')
      return
    }
  }

  analyzing.value = true

  try {
    // 调用 API 分析作品
    const result = await apiClient.learning.analyze({
      author,
      title,
      text
    })

    analyzedWorks.value.push({
      author,
      title,
      analyzed_at: new Date().toLocaleString(),
      analysis: result.data?.analysis || {}
    })

    ElMessage.success('作品分析完成！')

    // 清空表单
    if (uploadTab.value === 'text') {
      uploadForm.author = ''
      uploadForm.title = ''
      uploadForm.text = ''
    } else {
      fileForm.author = ''
      fileForm.title = ''
      clearConverted()
    }

  } catch (error) {
    ElMessage.error('分析失败：' + error.message)
  } finally {
    analyzing.value = false
  }
}

const viewWorkDetail = (work) => {
  selectedWork.value = work
  detailVisible.value = true
}

const applyStyle = (work) => {
  ElMessage.success(`已应用 ${work.author} - ${work.title} 的风格特征`)
  // 实际应该调用 API 应用风格
}

const deleteWork = async (work) => {
  try {
    await apiClient.learning.deleteWork(work.analysis_id)
    ElMessage.success('删除成功')
    // 从列表中移除
    const index = analyzedWorks.value.findIndex(w => w.analysis_id === work.analysis_id)
    if (index > -1) {
      analyzedWorks.value.splice(index, 1)
    }
  } catch (error) {
    ElMessage.error('删除失败：' + error.message)
  }
}

const generateReport = async () => {
  reportLoading.value = true
  
  try {
    const result = await apiClient.learning.getReport('default')
    if (result.data) {
      Object.assign(report, result.data)
    }
  } catch (error) {
    ElMessage.error('获取报告失败')
  } finally {
    reportLoading.value = false
  }
}

const loadAnalyzedWorks = async () => {
  try {
    const result = await apiClient.learning.getWorks()
    if (result.data && result.data.works) {
      analyzedWorks.value = result.data.works
    }
  } catch (error) {
    console.error('加载已分析作品失败:', error)
  }
}

onMounted(() => {
  generateReport()
  loadAnalyzedWorks()
})
</script>

<style scoped>
.learning-panel {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

ul {
  line-height: 2;
  padding-left: 20px;
}

/* Tab 样式 */
.upload-tabs {
  margin-bottom: 16px;
}

/* 上传区域样式 */
.upload-area {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  padding: 30px;
}

/* 转换预览 */
.converted-preview {
  width: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #909399;
}

/* 分析说明 */
:deep(.el-alert__content p) {
  margin: 4px 0;
}

:deep(.el-alert__content ul) {
  margin: 8px 0;
}

/* 文件列表样式 */
.file-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
