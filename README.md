# 多 Agent 协作小说系统

一个面向长篇小说创作的 AI 协作系统。当前仓库已经有可运行的后端、前端与核心数据流，不再是“纯设计稿”状态；最近已完成一轮工程收口，重点统一了配置、章节存储、前端路由与后端 API 模块化。

## 当前状态

- **版本**：v1.0
- **项目状态**：可开发、可本地运行、可继续重构
- **当前重点**：工程收口与稳定性提升
- **最近完成**：
  - 运行时配置统一到 SQLite + `config_service`
  - 章节存储统一到数据库真源
  - 前端切换到 `vue-router`
  - 后端 API 从单个大 `routes.py` 拆分为模块化路由
  - `novel / writing / learning` 已开始通过 service 层承载业务逻辑

## 核心能力

- 多角色协作小说创作
- 可配置 LLM 提供商（运行时配置）
- 小说、章节、人物、学习分析管理
- 前端控制台：配置、写作、学习、监控、派系、小说库
- 健康检查与基础任务管理

## 当前架构概览

### 前端

- Vue 3
- Vite
- Element Plus
- Pinia
- Vue Router

主要页面：

- `/dashboard` 首页
- `/auto` 全自动创作
- `/library` 小说仓库
- `/config` 项目配置
- `/monitor` Agent 监控
- `/writing` 写作面板
- `/learning` 学习中心
- `/schools` 派系库

### 后端

- FastAPI
- SQLite
- Redis / Celery（可选增强）
- service 层 + API 路由分层

当前 API 模块：

- `novel_routes.py`：小说 / 章节 / 人物 / 伏笔
- `config_routes.py`：配置 / LLM 校验 / LLM 测试
- `writing_routes.py`：写作流程与章节写作接口
- `learning_routes.py`：学习分析与学习报告
- `agent_routes.py`：Agent 状态与任务管理
- `ai_routes.py`：AI 辅助生成接口
- `auto_routes.py`：全自动创作
- `school_routes.py`：派系与风格融合
- `health.py`：健康检查

### service 层

当前已建立：

- `config_service.py`
- `chapter_service.py`
- `novel_service.py`
- `writing_service.py`
- `learning_service.py`

## 配置模型说明

这是当前项目最重要的约定之一：

### 1. `.env`
只用于**环境/基础设施配置**，例如：

- `REDIS_URL`
- `HOST`
- `PORT`
- `DEBUG`

### 2. SQLite（运行时配置真源）
运行中的业务配置统一保存在数据库中，由 `config_service` 负责访问：

- 默认 provider
- provider 配置
- API Key
- 项目配置

### 3. API Key 安全策略

- `/api/config` 不返回明文 API Key
- 前端只会收到：
  - `has_api_key`
  - `masked_api_key`
  - `api_key: ""`

## 章节存储模型说明

当前已统一为：

- **数据库为章节唯一真源**

也就是说：

- 小说仓库读写章节 → 数据库
- 写作接口读写章节 → 数据库

`file_manager` 仍然可以继续保留做：

- 导出
- 备份
- 快照

但不应再作为章节正文主存储。

## 本地开发启动

### 环境要求

- Python 3.10+
- Node.js 18+
- npm
- Redis（如果要启用 Celery）

## 后端启动

项目根目录已经有统一依赖文件：`requirements.txt`

### 1. 安装 Python 依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
```

### 2. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- `http://localhost:5173`

## Windows 快速检查脚本

仓库根目录提供：

- `setup-and-test.bat`

当前它会做：

1. 安装 Python 依赖
2. 执行部分 Python 语法检查
3. 运行 `backend/tests/test_all.py`

> 注意：这个 bat 目前更偏“快速烟测入口”，还不是完整 CI。

## Docker 运行说明

仓库提供了 `docker-compose.yml`，包含：

- `redis`
- `backend`
- `celery-worker`
- `celery-beat`（可选 profile）
- `frontend`（生产 profile）

### 启动基础服务

```bash
docker-compose up -d redis backend celery-worker
```

### 启动完整生产 profile

```bash
docker-compose --profile production up -d
```

### 当前 Docker 注意事项

- 已补充 `frontend/Dockerfile`
- Celery 仍属于增强能力，不是本地开发的必需前置
- 当前建议优先用“本地后端 + 本地前端”方式开发与调试

## 测试与验证

### 当前已补充的重点测试

- 配置统一测试
- 配置 API 测试
- 章节存储统一测试
- 路由注册测试
- service 委托测试

### 常用测试命令

在项目根目录执行：

```bash
python -m pytest backend/tests/test_config_service.py backend/tests/test_config_api.py backend/tests/test_chapter_storage.py backend/tests/test_route_registration.py backend/tests/test_service_routes.py -v
```

### CI

仓库已补充基础 GitHub Actions CI：

- 后端：安装依赖并运行核心 pytest 回归测试
- 前端：安装依赖并执行 `npm run build`

工作流文件：

```text
.github/workflows/ci.yml
```

### 前端构建验证

```bash
cd frontend
npm run build
```

## 当前项目结构

```text
novel-agent-system/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── setup-and-test.bat
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── novel_routes.py
│   │   │   ├── config_routes.py
│   │   │   ├── writing_routes.py
│   │   │   ├── learning_routes.py
│   │   │   ├── agent_routes.py
│   │   │   ├── ai_routes.py
│   │   │   ├── auto_routes.py
│   │   │   ├── school_routes.py
│   │   │   └── ws_routes.py
│   │   ├── services/
│   │   │   ├── config_service.py
│   │   │   ├── chapter_service.py
│   │   │   ├── novel_service.py
│   │   │   ├── writing_service.py
│   │   │   └── learning_service.py
│   │   ├── tasks/
│   │   ├── utils/
│   │   ├── config_db.py
│   │   ├── novel_db.py
│   │   ├── workflow_executor.py
│   │   └── main.py
│   └── tests/
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/
│       ├── router/
│       └── views/
├── docs/
│   └── superpowers/
│       └── plans/
├── data/
├── logs/
├── backups/
└── projects/
```

## 已知限制

当前项目虽然已经完成一轮重构，但仍有一些明确的待办：

1. Celery 结构仍偏增强能力，不建议当前阶段作为唯一执行路径
2. 仍存在一些依赖 warning：
   - FastAPI / Starlette 在 Python 3.14 下的 deprecation warning
3. 前端构建体积仍然偏大，建议继续做更细粒度拆包

## 建议开发顺序

如果继续推进，建议顺序如下：

1. 补 README / 启动文档（本次已更新）
2. 继续抽 `agent / ai / auto / school` service
3. 统一 API response schema
4. 清理技术债 warning
5. 完善 Docker / 部署链路
6. 增加更系统的 pytest / 前端测试 / CI

## 近期重构摘要

近期已完成的重要工程改造：

- 配置统一到 SQLite + `config_service`
- API Key 脱敏输出
- 章节存储统一到数据库
- 前端接入 `vue-router`
- 超大 `routes.py` 拆分并删除
- 建立 `novel / writing / learning` service 层
- 建立 `agent / ai / auto / school` service 层
- 统一核心 API success/error 响应结构
- 补充 `frontend/Dockerfile`

## 许可证

MIT License
