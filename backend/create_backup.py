import requests
import json
from datetime import datetime

print('正在收集软件参数...\n')

# 1. 收集配置信息
print('1. 收集 LLM 配置...')
config_r = requests.get('http://localhost:8000/api/config')
config = config_r.json()

# 2. 收集小说信息
print('2. 收集小说数据...')
novels_r = requests.get('http://localhost:8000/api/novels')
novels = novels_r.json()['data']['novels']

# 3. 收集模板信息
print('3. 收集创作模板...')
templates_r = requests.get('http://localhost:8000/api/ai/templates')
templates = templates_r.json()

# 4. 收集 API 端点
print('4. 收集 API 端点...')
api_endpoints = {
    'health': '/api/health',
    'config': '/api/config',
    'novels': '/api/novels',
    'auto_create': '/api/auto/create',
    'ai_templates': '/api/ai/templates',
    'ai_generate_outline': '/api/ai/generate-outline',
    'ai_generate_characters': '/api/ai/generate-characters',
    'ai_generate_chapter_outline': '/api/ai/generate-chapter-outline',
    'ai_generate_plot': '/api/generate-plot',
}

# 生成备份文档
backup_content = f'''# 📊 多 Agent 协作小说系统 - 参数备份

**备份时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: v1.0.8  
**状态**: ✅ 生产就绪

---

## 1. LLM 配置

### 默认提供商
```json
{json.dumps(config['data']['default_provider'], ensure_ascii=False, indent=2)}
```

### 提供商配置
```json
{json.dumps(config['data']['providers'], ensure_ascii=False, indent=2)}
```

### 配置详情
- **eggfans**
  - API Key: `sk-***{config['data']['providers']['eggfans']['api_key'][-4:]}`
  - Base URL: `{config['data']['providers']['eggfans']['base_url']}`
  - Model: `{config['data']['providers']['eggfans']['model']}`
  - Timeout: 300 秒

---

## 2. 小说数据

### 统计信息
- **小说总数**: {len(novels)} 本
- **总章节数**: {sum(n.get('total_chapters', 0) for n in novels)} 章
- **总字数**: {sum(n.get('total_words', 0) for n in novels)} 字

### 小说列表
| # | 书名 | 类型 | 章节数 | 总字数 | 状态 |
|---|------|------|--------|--------|------|
'''

for i, novel in enumerate(novels, 1):
    backup_content += f"| {i} | {novel['title']} | {novel.get('genre', 'N/A')} | {novel.get('total_chapters', 0)} | {novel.get('total_words', 0)} | {novel.get('status', 'N/A')} |\n"

backup_content += f'''
---

## 3. 创作模板

### 模板统计
- **大纲模板**: {len(templates['data']['outline'])} 个
- **人物模板**: {len(templates['data']['character'])} 个
- **章节模板**: {len(templates['data']['chapter'])} 个
- **情节模板**: {len(templates['data']['plot'])} 个
- **总计**: {sum(len(v) for v in templates['data'].values())} 个

### 大纲模板
'''

for template in templates['data']['outline']:
    backup_content += f'''
#### {template['name']} ({template['id']})
**适用**: {template.get('description', 'N/A')}
'''

backup_content += f'''
### 人物模板
'''

for template in templates['data']['character']:
    backup_content += f'''
#### {template['name']} ({template['id']})
**适用**: {template.get('description', 'N/A')}
'''

backup_content += f'''
### 章节模板
'''

for template in templates['data']['chapter']:
    backup_content += f'''
#### {template['name']} ({template['id']})
**适用**: {template.get('description', 'N/A')}
'''

backup_content += f'''
### 情节模板
'''

for template in templates['data']['plot']:
    backup_content += f'''
#### {template['name']} ({template['id']})
**适用**: {template.get('description', 'N/A')}
'''

backup_content += f'''

---

## 4. API 端点

| 功能 | 端点 | 方法 |
|------|------|------|
'''

for name, endpoint in api_endpoints.items():
    method = 'GET' if 'health' in name or 'templates' in name or 'config' in name or name == 'novels' else 'POST'
    backup_content += f"| {name} | `{endpoint}` | {method} |\n"

backup_content += f'''

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

**备份完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**备份文件**: `SYSTEM_PARAMS_BACKUP.md`
'''

# 保存备份文件
with open('D:/new test/novel-agent-system/SYSTEM_PARAMS_BACKUP.md', 'w', encoding='utf-8') as f:
    f.write(backup_content)

print(f'\n✅ 备份完成！')
print(f'文件位置：D:/new test/novel-agent-system/SYSTEM_PARAMS_BACKUP.md')
print(f'\n统计信息:')
print(f'  - 小说：{len(novels)} 本')
print(f'  - 模板：{sum(len(v) for v in templates["data"].values())} 个')
print(f'  - API 端点：{len(api_endpoints)} 个')
