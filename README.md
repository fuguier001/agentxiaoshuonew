# 多 Agent 协作小说系统

一个面向长篇小说创作的 AI 协作系统，支持全自动创作、蓝图管理、章节重写等功能。

## 当前状态

- **版本**：v1.2
- **项目状态**：生产就绪
- **最近更新**：2026-03-27

## 核心能力

### 🤖 全自动创作
- 一键生成完整小说（世界观 + 3000章规划 + 第一章）
- 断点续传支持
- 实时进度跟踪

### 📋 蓝图管理
- 世界观设定（world_map）
- 宏观剧情规划（macro_plot）
- 人物体系（character_system）
- 伏笔网络（hook_network）
- AI 润色支持（空蓝图可自动生成）
- **蓝图预览器**：4标签页可视化展示（世界观/章节规划/人物/伏笔）

### ✍️ 章节管理
- 章节重写（异步任务队列）
- 小说续写
- 草稿/已发布状态
- **小说查看器 Tabs 结构**：章节列表/蓝图预览/续写功能集成在同一对话框

### ⚙️ 多 LLM 提供商
- 智谱AI（GLM-5-Turbo）
- EggFans（deepseek-v3.2）
- 火山引擎
- 阿里云
- 自定义 OpenAI 兼容接口

## 架构概览

### 前端 (Vue 3)

```
frontend/
├── src/
│   ├── api/client.js          # API 客户端
│   ├── router/                 # 路由配置
│   ├── views/
│   │   ├── AutoCreation.vue   # 全自动创作
│   │   ├── NovelLibrary.vue   # 小说仓库
│   │   ├── ProjectConfig.vue  # 项目配置
│   │   ├── AgentMonitor.vue   # Agent 监控
│   │   └── ...
│   └── components/
│       └── BlueprintViewer.vue # 蓝图查看器
```

### 后端 (FastAPI)

```
backend/
├── app/
│   ├── api/                    # API 路由
│   │   ├── novel_routes.py     # 小说/章节/蓝图/续写
│   │   ├── config_routes.py    # 配置/LLM 测试
│   │   ├── auto_routes.py      # 全自动创作
│   │   └── ...
│   ├── services/               # 业务服务
│   │   ├── config_service.py   # 配置管理
│   │   ├── novel_service.py    # 小说管理
│   │   ├── chapter_service.py  # 章节管理
│   │   └── auto_service.py     # 自动创作
│   ├── agents/                 # Agent 系统
│   │   ├── registry.py         # Agent 注册表
│   │   ├── writer_agent.py
│   │   ├── plot_agent.py
│   │   └── ...
│   ├── novel_db.py             # 小说数据库
│   ├── config_db.py            # 配置数据库
│   ├── workflow_executor.py    # 工作流执行器
│   └── novel_architect.py      # 小说架构师
└── data/
    ├── novels.db               # 小说数据库
    └── config.db               # 配置数据库
```

## API 文档

### 小说管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels` | 获取小说列表（支持分页） |
| POST | `/api/novels` | 创建小说 |
| GET | `/api/novels/{id}` | 获取小说详情 |
| PUT | `/api/novels/{id}` | 更新小说 |
| DELETE | `/api/novels/{id}` | 删除小说（移至回收站） |

### 蓝图管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/blueprint` | 获取蓝图 |
| PUT | `/api/novels/{id}/blueprint` | 更新蓝图 |
| POST | `/api/novels/{id}/blueprint/polish` | AI 润色蓝图 |

### 章节管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/chapters` | 获取章节列表（支持分页） |
| POST | `/api/novels/{id}/chapters` | 创建章节 |
| GET | `/api/novels/{id}/chapters/{num}` | 获取章节详情 |
| PUT | `/api/novels/{id}/chapters/{num}` | 更新章节 |
| POST | `/api/novels/{id}/chapters/{num}/rewrite` | 重写章节（异步） |

### 导出功能

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/export/txt` | 导出小说为 TXT 文件下载 |

### 任务队列

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}` | 获取任务状态 |
| GET | `/api/queue/status` | 获取队列状态 |

### 全自动创作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auto/create` | 开始全自动创作 |
| GET | `/api/auto/progress/{title}` | 获取创作进度 |
| GET | `/api/auto/checkpoint/{title}` | 获取断点状态 |

## 配置说明

### LLM 提供商配置

不同提供商使用不同的 endpoint：

| 提供商 | Base URL | Endpoint |
|--------|----------|----------|
| 智谱AI | `https://open.bigmodel.cn/api/paas/v4` | `/chat/completions` |
| EggFans | `https://eggfans.com` | `/v1/chat/completions` |
| 阿里云 | `https://dashscope.aliyuncs.com/api/v1` | 自定义 |

### API Key 安全

- API Key 不返回明文
- 前端只显示 `has_api_key` 和 `masked_api_key`（如 `***YkUl`）
- 更新时传空字符串保留原密钥

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 访问地址

- 前端：`http://localhost:5173`
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

## 开发指南

### 统一响应格式

```python
# 成功响应
{
    "success": true,
    "status": "success",
    "data": {...},
    "message": "操作成功"
}

# 错误响应
{
    "success": false,
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {...}
    }
}
```

### 分页参数

```
GET /api/novels?page=1&page_size=20

Response:
{
    "data": {
        "novels": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

### 任务队列

系统使用串行任务队列，避免 API 并发问题：

1. 提交任务 → 返回 `task_id`
2. 轮询 `/api/tasks/{task_id}` 获取状态
3. 状态：`queued` → `running` → `completed` / `failed`

## 测试

```bash
# 运行测试
cd backend
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_config_service.py -v
```

## 已知问题

1. 部分异步测试需要 `@pytest.mark.asyncio` 装饰器
2. 前端构建体积较大，建议代码分割

## 更新日志

### v1.2 (2026-03-27)

**新功能**
- 蓝图 AI 润色支持空内容自动生成
- 蓝图预览器（4标签页可视化展示）
- 章节重写异步任务队列
- 小说续写功能
- **TXT 导出功能**（支持 UTF-8 编码、中文文件名）
- 多 LLM 提供商 endpoint 配置
- 任务队列自动清理（1小时过期）

**改进**
- 统一错误处理（移除 HTTPException）
- 蓝图 API Pydantic 输入验证
- 列表 API 分页支持
- Agent 状态实时更新
- **小说查看器重构为 Tabs 结构**：章节/蓝图/续写集成在同一对话框

**修复**
- bigmodel endpoint 路径错误
- 配置保存 500 错误
- 章节状态显示

### v1.1 (2026-03-26)

- 配置统一到 SQLite
- API Key 脱敏输出
- 章节存储统一到数据库
- 前端接入 vue-router
- API 模块化拆分

## 许可证

MIT License
