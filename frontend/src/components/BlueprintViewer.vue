<template>
  <div class="blueprint-viewer">
    <div v-if="!data || Object.keys(data).length === 0" class="empty-state">
      <el-empty description="暂无数据" :image-size="100" />
    </div>

    <div v-else class="blueprint-content">
      <!-- 世界观 -->
      <template v-if="type === 'world_map'">
        <div class="section">
          <h4>🌍 世界名称</h4>
          <p>{{ data.world_name || '未设定' }}</p>
        </div>
        <div class="section" v-if="data.power_system">
          <h4>⚡ 力量体系</h4>
          <p><strong>体系名称：</strong>{{ data.power_system.name || '未设定' }}</p>
          <p><strong>等级：</strong></p>
          <ul>
            <li v-for="(level, idx) in (data.power_system.levels || [])" :key="idx">{{ level }}</li>
          </ul>
        </div>
        <div class="section" v-if="data.main_factions">
          <h4>🏛️ 主要势力</h4>
          <el-tag v-for="(faction, idx) in data.main_factions" :key="idx" style="margin: 5px;">
            {{ faction.name }}: {{ faction.description }}
          </el-tag>
        </div>
        <div class="section" v-if="data.background">
          <h4>📜 世界背景</h4>
          <p>{{ data.background }}</p>
        </div>
      </template>

      <!-- 宏观规划 -->
      <template v-else-if="type === 'macro_plot'">
        <div class="section" v-if="data.total_chapters">
          <el-tag type="primary">共 {{ data.total_chapters }} 章</el-tag>
        </div>
        <div class="section" v-for="(volume, idx) in (data.volumes || [])" :key="idx">
          <h4>📚 {{ volume.title }}</h4>
          <p><strong>章节范围：</strong>第 {{ volume.start_chapter }} - {{ volume.end_chapter }} 章</p>
          <p>{{ volume.outline }}</p>
        </div>
      </template>

      <!-- 人物体系 -->
      <template v-else-if="type === 'character_system'">
        <div class="section" v-if="data.protagonist">
          <h4>👤 主角</h4>
          <p><strong>姓名：</strong>{{ data.protagonist.name }}</p>
          <p>{{ data.protagonist.background }}</p>
        </div>
        <div class="section" v-if="data.supporting_characters">
          <h4>👥 配角</h4>
          <el-tag v-for="(char, idx) in data.supporting_characters" :key="idx" style="margin: 5px;">
            {{ char.name }} - {{ char.role }}
          </el-tag>
        </div>
        <div class="section" v-if="data.antagonists">
          <h4>😈 反派</h4>
          <el-tag v-for="(char, idx) in data.antagonists" :key="idx" type="danger" style="margin: 5px;">
            {{ char.name }} - {{ char.role }}
          </el-tag>
        </div>
      </template>

      <!-- 伏笔网络 -->
      <template v-else-if="type === 'hook_network'">
        <div class="section" v-for="(hook, idx) in (data.hooks || [])" :key="idx">
          <el-card shadow="hover" style="margin-bottom: 10px;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ hook.description }}</span>
                <el-tag :type="hook.status === 'resolved' ? 'success' : 'warning'">
                  {{ hook.status === 'resolved' ? '已解决' : '未解决' }}
                </el-tag>
              </div>
            </template>
            <p><strong>类型：</strong>{{ hook.hook_type }}</p>
            <p><strong>引入章节：</strong>第 {{ hook.chapter_introduced }} 章</p>
            <p v-if="hook.resolved_chapter"><strong>解决章节：</strong>第 {{ hook.resolved_chapter }} 章</p>
          </el-card>
        </div>
      </template>

      <!-- 未知类型，显示原始 JSON -->
      <template v-else>
        <pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">{{ JSON.stringify(data, null, 2) }}</pre>
      </template>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  type: {
    type: String,
    default: 'unknown'
  }
})
</script>

<style scoped>
.blueprint-viewer {
  max-height: 500px;
  overflow-y: auto;
}

.blueprint-content {
  padding: 10px;
}

.section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.section p {
  margin: 5px 0;
  color: #606266;
  line-height: 1.6;
}

.section ul {
  margin: 5px 0;
  padding-left: 20px;
}

.section li {
  margin: 3px 0;
  color: #606266;
}

.empty-state {
  padding: 40px;
  text-align: center;
}
</style>
