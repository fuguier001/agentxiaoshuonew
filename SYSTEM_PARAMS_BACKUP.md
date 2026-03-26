# 📊 多 Agent 协作小说系统 - 参数备份

**备份时间**: 2026-03-22 22:38:44  
**版本**: v1.0.8  
**状态**: ✅ 生产就绪

---

## 1. LLM 配置

### 默认提供商
```json
"eggfans"
```

### 提供商配置
```json
{
  "eggfans": {
    "api_format": "openai",
    "api_key": "sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8HusmDnatZ93U1",
    "base_url": "https://eggfans.com",
    "endpoint": "/v1/chat/completions",
    "model": "deepseek-v3.2",
    "auth_type": "bearer",
    "auth_header": null,
    "timeout": 60,
    "enabled": true,
    "rate_limit": null
  },
  "volcengine": {
    "api_format": "openai",
    "api_key": "",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "endpoint": "/v1/chat/completions",
    "model": "",
    "auth_type": "bearer",
    "auth_header": null,
    "timeout": 60,
    "enabled": true,
    "rate_limit": null
  },
  "aliyun": {
    "api_format": "aliyun",
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "endpoint": "/v1/chat/completions",
    "model": "",
    "auth_type": "bearer",
    "auth_header": null,
    "timeout": 60,
    "enabled": true,
    "rate_limit": null
  }
}
```

### 配置详情
- **eggfans**
  - API Key: `sk-***93U1`
  - Base URL: `https://eggfans.com`
  - Model: `deepseek-v3.2`
  - Timeout: 300 秒

---

## 2. 小说数据

### 统计信息
- **小说总数**: 1 本
- **总章节数**: 1 章
- **总字数**: 2232 字

### 小说列表
| # | 书名 | 类型 | 章节数 | 总字数 | 状态 |
|---|------|------|--------|--------|------|
| 1 | 测试章节保存 | 玄幻 | 1 | 2232 | ongoing |

---

## 3. 创作模板

### 模板统计
- **大纲模板**: 5 个
- **人物模板**: 3 个
- **章节模板**: 3 个
- **情节模板**: 2 个
- **总计**: 13 个

### 大纲模板

#### 三幕式结构 (three_act)
**适用**: 经典好莱坞三幕式结构，适合商业小说

#### 英雄之旅 (heros_journey)
**适用**: 约瑟夫·坎贝尔英雄之旅模板，适合奇幻/冒险小说

#### 起承转合 (qichengzhuanhe)
**适用**: 中国传统叙事结构，适合武侠/历史/言情小说

#### 多线叙事 (multi_thread)
**适用**: 多线并行叙事，适合悬疑/群像/宏大题材

#### 单元剧结构 (unit_drama)
**适用**: 独立单元 + 主线贯穿，适合侦探/灵异/都市传说

### 人物模板

#### 主角模板 (深度) (protagonist)
**适用**: 深度刻画主角，适合第一主角

#### 反派模板 (antagonist)
**适用**: 塑造有深度的反派，避免脸谱化

#### 配角模板 (supporting)
**适用**: 功能性配角设计

### 章节模板

#### 开篇章节模板 (opening)
**适用**: 小说开头 1-3 章专用

#### 发展章节模板 (development)
**适用**: 故事发展阶段的章节

#### 高潮章节模板 (climax)
**适用**: 故事高潮章节专用

### 情节模板

#### 冲突升级模板 (conflict_escalation)
**适用**: 设计逐步升级的冲突

#### 悬念设置模板 (suspense)
**适用**: 设计吸引人的悬念


---

## 4. API 端点

| 功能 | 端点 | 方法 |
|------|------|------|
| health | `/api/health` | GET |
| config | `/api/config` | GET |
| novels | `/api/novels` | GET |
| auto_create | `/api/auto/create` | POST |
| ai_templates | `/api/ai/templates` | GET |
| ai_generate_outline | `/api/ai/generate-outline` | POST |
| ai_generate_characters | `/api/ai/generate-characters` | POST |
| ai_generate_chapter_outline | `/api/ai/generate-chapter-outline` | POST |
| ai_generate_plot | `/api/generate-plot` | POST |


---

## 5. 工作流配置

### 章节创作工作流（6 步）
1. **剧情架构师** - 细化大纲
2. **人物设计师** - 准备角色
3. **章节写手** - 撰写初稿
4. **对话专家** - 打磨对话
5. **审核编辑** - 一致性检查
6. **主编** - 最终审核

### 超时配置
- **LLM API 超时**: 300 秒（5 分钟）
- **重试机制**: 最多 3 次，间隔 5 秒

---

## 6. 数据库配置

### 数据库文件
- **配置数据库**: `backend/data/config.db`
- **小说数据库**: `backend/data/novels.db`

### 数据表
- **llm_providers** - LLM 提供商配置
- **system_config** - 系统配置
- **project_config** - 项目配置
- **novels** - 小说信息
- **chapters** - 章节信息
- **characters** - 人物信息
- **plot_hooks** - 伏笔信息
- **style_fusions** - 风格融合信息

---

## 7. 前端配置

### 服务地址
- **前端**: http://localhost:5173
- **后端**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 页面路由
| 页面 | 路由 | 功能 |
|------|------|------|
| 首页 | `/` | 系统概览 |
| 全自动创作 | `/auto` | AI 全自动创作 |
| 小说仓库 | `/library` | 小说管理 |
| 项目配置 | `/config` | LLM 配置 |
| Agent 监控 | `/monitor` | Agent 状态 |
| 写作面板 | `/writing` | 手动创作 |
| 学习中心 | `/learning` | 学习分析 |
| 派系库 | `/schools` | 风格管理 |

---

## 8. 功能清单

### ✅ 已完成功能
- [x] 全自动 AI 创作（世界观 + 规划 + 人物 + 伏笔 + 章节）
- [x] 小说仓库管理（查看/编辑/删除/批量操作）
- [x] 批量下载（TXT/Markdown）
- [x] 专业创作模板（22 个）
- [x] 6 步工作流创作
- [x] 数据持久化（SQLite）
- [x] LLM 配置管理
- [x] 重试机制（3 次）
- [x] 超时优化（300 秒）

### 📊 系统统计
- **代码文件**: ~50 个
- **前端页面**: 8 个
- **API 端点**: 20+ 个
- **数据库表**: 8 个
- **创作模板**: 22 个

---

## 9. 性能指标

### 创作速度
- **单章耗时**: 约 6 分钟（6 步完整流程）
- **10 章耗时**: 约 60 分钟
- **大纲生成**: 约 1-2 分钟
- **人物生成**: 约 1-2 分钟

### 质量指标
- **单章字数**: 2000-3000 字
- **大纲字数**: 1500-2000 字
- **人物设定**: 2000-3000 字

---

## 10. 环境变量

### 必需配置
- **LLM API Key**: eggfans API Key
- **LLM Base URL**: https://eggfans.com
- **LLM Model**: deepseek-v3.2

### 可选配置
- **超时时间**: 300 秒（默认）
- **重试次数**: 3 次（默认）
- **重试间隔**: 5 秒（默认）

---

**备份完成时间**: 2026-03-22 22:38:44  
**备份文件**: `SYSTEM_PARAMS_BACKUP.md`
