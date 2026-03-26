# 多 Agent 协作小说系统 - 实施计划

**创建日期**: 2026-03-21  
**版本**: v1.0  
**状态**: 待实施

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [系统架构](#3-系统架构)
4. [核心模块设计](#4-核心模块设计)
5. [实施阶段](#5-实施阶段)
6. [风险评估](#6-风险评估)
7. [验收标准](#7-验收标准)

---

## 1. 项目概述

### 1.1 项目目标

构建一个**多 Agent 协作的小说创作系统**，能够：
- 模拟真实写作工作室的协作流程
- 从外部作品学习写作技巧和风格
- 自主进化写作风格，越写越好
- 保持长篇小说的情节连贯性和角色一致性
- 自动保存到本地，支持版本控制

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **7 大 Agent 协作** | 主编、剧情、人物、写手、对话、审核、学习 |
| **三层记忆系统** | 短期 (章节) + 中期 (卷) + 长期 (全书) |
| **四层学习记忆** | 原始→模式→技巧→风格 |
| **派系分类系统** | 按类型/文笔/节奏分类，支持融合 |
| **可配置 LLM** | 火山/阿里云/eggfans 完全可配置 |
| **本地保存** | 自动保存 + Git 版本控制 |

### 1.3 用户故事

```
作为用户，我希望：
- 配置自己的 LLM API 密钥（火山/阿里云/eggfans）
- 上传喜欢的小说让系统学习风格
- 选择或融合派系风格应用到写作
- 输入章节大纲，系统自动创作
- 实时查看 Agent 工作状态
- 自动保存章节到本地文件夹
- 查看学习报告和风格进化历史
```

---

## 2. 技术栈

### 2.1 后端

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| 语言 | Python | 3.10+ |
| Web 框架 | FastAPI | 最新 |
| 异步服务器 | uvicorn | 最新 |
| 任务队列 | Celery | 5.3+ |
| 消息代理 | Redis | 7.0+ |
| 向量数据库 | Chroma | 最新 |
| 知识图谱 | NetworkX | 最新 |
| 关系数据库 | SQLite | 内置 |
| Git 封装 | GitPython | 最新 |
| HTTP 客户端 | httpx | 最新 |

### 2.2 前端

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| 框架 | Vue 3 | 3.4+ |
| 构建工具 | Vite | 5.0+ |
| UI 组件库 | Element Plus | 最新 |
| 状态管理 | Pinia | 最新 |
| HTTP 客户端 | axios | 最新 |
| WebSocket | 原生 | - |

### 2.3 部署

| 组件 | 技术选型 |
|------|----------|
| 容器化 | Docker + docker-compose |
| 反向代理 | Nginx (可选) |
| 进程管理 | systemd / PM2 |

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        多 Agent 协作小说系统                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    前端控制台 (Vue 3)                     │    │
│  │  - 项目配置  - Agent 监控  - 写作面板  - 学习中心  - 派系库  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↑↓ WebSocket + REST API            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              后端核心 (Python + FastAPI)                  │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │                  API 网关层                         │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                              ↑↓                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │              任务编排层 (Celery + Redis)            │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                              ↑↓                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │                 7 大 Agent 核心层                    │  │    │
│  │  │  主编 | 剧情 | 人物 | 写手 | 对话 | 审核 | 学习       │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                              ↑↓                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │                  记忆引擎层                         │  │    │
│  │  │  短期记忆 | 中期记忆 | 长期记忆 | 派系注册表          │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                              ↑↓                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │                  存储层                            │  │    │
│  │  │  本地文件 | 向量库 | 知识图谱 | SQLite              │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
novel-agent-system/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── config.py               # 配置管理
│   │   │
│   │   ├── api/                    # API 路由
│   │   │   ├── routes.py           # REST API
│   │   │   ├── websocket.py        # 实时日志
│   │   │   └── school_routes.py    # 派系 API
│   │   │
│   │   ├── agents/                 # 7 大 Agent
│   │   │   ├── base_agent.py       # 基类
│   │   │   ├── registry.py         # 注册表
│   │   │   ├── editor_agent.py     # 主编
│   │   │   ├── plot_agent.py       # 剧情
│   │   │   ├── character_agent.py  # 人物
│   │   │   ├── writer_agent.py     # 写手
│   │   │   ├── dialogue_agent.py   # 对话
│   │   │   ├── reviewer_agent.py   # 审核
│   │   │   └── learning_agent.py   # 学习
│   │   │
│   │   ├── memory/                 # 记忆引擎
│   │   │   ├── memory_engine.py    # 统一接口
│   │   │   ├── short_term.py       # 短期记忆
│   │   │   ├── mid_term.py         # 中期记忆
│   │   │   ├── long_term.py        # 长期记忆
│   │   │   ├── style_library.py    # 风格库
│   │   │   └── school_registry.py  # 派系注册表
│   │   │
│   │   ├── tasks/                  # Celery 任务
│   │   │   ├── celery_app.py
│   │   │   └── agent_tasks.py      # 工作流编排
│   │   │
│   │   ├── storage/                # 文件存储
│   │   │   ├── file_manager.py
│   │   │   ├── version_control.py  # Git 封装
│   │   │   └── exporter.py         # 导出 EPUB/TXT
│   │   │
│   │   └── utils/
│   │       ├── llm_client.py       # 统一 LLM 调用
│   │       └── logger.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── ProjectConfig.vue   # API 配置
│   │   │   ├── AgentMonitor.vue
│   │   │   ├── WritingPanel.vue
│   │   │   ├── LearningPanel.vue   # 学习中心
│   │   │   └── SchoolRegistry.vue  # 派系库
│   │   └── api/client.js
│   │
│   └── package.json
│
├── projects/                       # 小说项目存储
│   └── [小说名]/
│       ├── config.json
│       ├── outline/
│       ├── characters/
│       ├── chapters/
│       ├── drafts/
│       ├── memory/
│       └── exports/
│
└── data/
    ├── vector_db/
    ├── knowledge_graph/
    ├── styles/
    ├── fused_styles/
    └── schools/
```

---

## 4. 核心模块设计

### 4.1 Agent 基类

```python
# backend/app/agents/base_agent.py
class BaseAgent(ABC):
    """所有 Agent 的基类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.llm_client = None
        self.memory_engine = None
        self.state = "idle"  # idle | working | error
        self.last_active = None
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务 - 每个 Agent 实现自己的逻辑"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """返回该 Agent 的系统提示词"""
        pass
    
    async def call_llm(self, prompt: str, **kwargs) -> str:
        """统一 LLM 调用入口"""
        pass
    
    async def read_memory(self, query: str, limit: int = 5) -> list:
        """从记忆引擎读取相关上下文"""
        pass
    
    async def write_memory(self, content: str, metadata: Dict[str, Any]):
        """写入新内容到记忆"""
        pass
    
    def log(self, message: str, level: str = "info"):
        """统一日志输出"""
        pass
```

### 4.2 记忆引擎接口

```python
# backend/app/memory/memory_engine.py
class MemoryEngine:
    """三层记忆系统统一接口"""
    
    async def retrieve(self, query: str, limit: int = 5, context_type: str = "all") -> List[Dict]:
        """多路召回检索"""
        pass
    
    async def store(self, content: str, metadata: Dict[str, Any]):
        """写入新内容，自动分发到三层记忆"""
        pass
    
    async def get_character_state(self, character_name: str) -> Dict[str, Any]:
        """查询角色当前状态"""
        pass
    
    async def get_unresolved_plot_threads(self) -> List[Dict]:
        """获取未回收的伏笔列表"""
        pass
    
    async def check_consistency(self, content: str) -> List[Dict]:
        """检查内容一致性"""
        pass
```

### 4.3 LLM 客户端

```python
# backend/app/utils/llm_client.py
class LLMClient:
    """通用 LLM 调用客户端"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "./config/llm_providers.json"
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.default_provider: Optional[str] = None
    
    def load_config(self):
        """从 JSON 配置文件加载所有提供商配置"""
        pass
    
    async def generate(self, prompt: str, system_prompt: str,
                       provider: Optional[str] = None, **kwargs) -> str:
        """调用 LLM 生成内容"""
        pass
    
    async def test_connection(self, provider: str) -> Dict[str, Any]:
        """测试 API 连接"""
        pass
```

### 4.4 派系注册表

```python
# backend/app/memory/school_registry.py
class SchoolRegistry:
    """派系注册表"""
    
    async def register_learned_style(self, style_data: Dict[str, Any]) -> str:
        """将从作品学习到的风格注册到对应派系"""
        pass
    
    async def check_fusion_compatibility(self, school_ids: List[str]) -> Dict[str, Any]:
        """检查多个派系融合的兼容性"""
        pass
    
    async def fuse_schools(self, school_ids: List[str], 
                          fusion_name: str,
                          weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """融合多个派系创建新风格"""
        pass
```

---

## 5. 实施阶段

### 阶段 1: 基础框架 (预计 1-2 周)

**目标**: 搭建项目脚手架，打通基础通信

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 1.1 | 创建项目目录结构 | P0 | 2h | ⬜ |
| 1.2 | 编写 requirements.txt | P0 | 1h | ⬜ |
| 1.3 | 编写 docker-compose.yml | P0 | 2h | ⬜ |
| 1.4 | FastAPI 后端脚手架 | P0 | 4h | ⬜ |
| 1.5 | Vue 3 前端脚手架 | P0 | 4h | ⬜ |
| 1.6 | 配置管理模块 (config.py) | P0 | 3h | ⬜ |
| 1.7 | LLM 客户端基础实现 | P0 | 6h | ⬜ |
| 1.8 | Agent 基类实现 | P0 | 4h | ⬜ |
| 1.9 | Agent 注册表实现 | P0 | 3h | ⬜ |
| 1.10 | 基础记忆引擎 (短期记忆) | P1 | 6h | ⬜ |

**验收标准**:
- [ ] 项目可以启动 (后端 + 前端)
- [ ] 可以配置 LLM API 密钥
- [ ] 可以测试 API 连接
- [ ] Agent 基类可以实例化

---

### 阶段 2: Agent 实现 (预计 2-3 周)

**目标**: 完成 7 大 Agent 核心逻辑，打通写作工作流

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 2.1 | LearningAgent 实现 | P0 | 8h | ⬜ |
| 2.2 | PlotAgent 实现 | P0 | 6h | ⬜ |
| 2.3 | CharacterAgent 实现 | P0 | 6h | ⬜ |
| 2.4 | WriterAgent 实现 | P0 | 8h | ⬜ |
| 2.5 | DialogueAgent 实现 | P0 | 6h | ⬜ |
| 2.6 | ReviewerAgent 实现 | P0 | 6h | ⬜ |
| 2.7 | EditorAgent 实现 | P0 | 6h | ⬜ |
| 2.8 | Celery 任务编排 | P0 | 8h | ⬜ |
| 2.9 | 章节创作工作流 | P0 | 8h | ⬜ |
| 2.10 | 文件存储模块 | P0 | 4h | ⬜ |
| 2.11 | Git 版本控制集成 | P1 | 4h | ⬜ |
| 2.12 | WebSocket 实时日志 | P1 | 6h | ⬜ |

**验收标准**:
- [ ] 输入大纲可以自动生成章节
- [ ] 7 大 Agent 按工作流执行
- [ ] 章节自动保存到本地
- [ ] 前端可以查看 Agent 状态

---

### 阶段 3: 学习系统 (预计 2-3 周)

**目标**: 实现四层学习记忆，打通学习闭环

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 3.1 | 长期记忆 (向量数据库) | P0 | 8h | ⬜ |
| 3.2 | 长期记忆 (知识图谱) | P0 | 8h | ⬜ |
| 3.3 | 长期记忆 (时间线索引) | P0 | 6h | ⬜ |
| 3.4 | 风格库实现 (style_library.py) | P0 | 6h | ⬜ |
| 3.5 | LearningAgent 作品分析 | P0 | 8h | ⬜ |
| 3.6 | 模式提取 (L2) | P0 | 6h | ⬜ |
| 3.7 | 技巧抽象 (L3) | P0 | 6h | ⬜ |
| 3.8 | 风格融合 (L4) | P0 | 6h | ⬜ |
| 3.9 | 写作时记忆检索 | P0 | 6h | ⬜ |
| 3.10 | 学习闭环 (反馈→更新) | P0 | 6h | ⬜ |
| 3.11 | 学习报告生成 | P1 | 4h | ⬜ |

**验收标准**:
- [ ] 可以上传小说进行分析
- [ ] 分析结果存入四层记忆
- [ ] 写作时自动检索学习记忆
- [ ] 章节完成后自动评估更新

---

### 阶段 4: 派系系统 (预计 1-2 周)

**目标**: 实现派系分类、兼容性检查、融合功能

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 4.1 | 派系注册表数据结构 | P0 | 4h | ⬜ |
| 4.2 | 默认派系模板初始化 | P0 | 4h | ⬜ |
| 4.3 | 自动分类到派系 | P0 | 6h | ⬜ |
| 4.4 | 兼容性检查算法 | P0 | 6h | ⬜ |
| 4.5 | 派系融合 LLM 调用 | P0 | 6h | ⬜ |
| 4.6 | 融合风格存储 | P0 | 3h | ⬜ |
| 4.7 | 派系 API 路由 | P0 | 4h | ⬜ |

**验收标准**:
- [ ] 可以查看派系列表
- [ ] 可以检查派系兼容性
- [ ] 可以融合派系创建新风格
- [ ] 可以应用派系风格到写作

---

### 阶段 5: 前端完善 (预计 1-2 周)

**目标**: 完成所有管理界面，实现实时日志

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 5.1 | Dashboard 首页 | P0 | 6h | ⬜ |
| 5.2 | ProjectConfig 配置页 | P0 | 8h | ⬜ |
| 5.3 | AgentMonitor 监控页 | P0 | 6h | ⬜ |
| 5.4 | WritingPanel 写作页 | P0 | 8h | ⬜ |
| 5.5 | LearningPanel 学习页 | P0 | 8h | ⬜ |
| 5.6 | SchoolRegistry 派系页 | P0 | 8h | ⬜ |
| 5.7 | WebSocket 实时日志 | P0 | 6h | ⬜ |
| 5.8 | 测试面板 | P1 | 4h | ⬜ |

**验收标准**:
- [ ] 所有配置界面可用
- [ ] 可以实时查看 Agent 状态
- [ ] 可以上传作品学习
- [ ] 可以管理派系融合

---

### 阶段 6: 测试优化 (预计 1-2 周)

**目标**: 端到端测试，性能优化，文档完善

#### 任务清单

| ID | 任务 | 优先级 | 预计工时 | 状态 |
|----|------|--------|----------|------|
| 6.1 | 单元测试编写 | P0 | 8h | ⬜ |
| 6.2 | 集成测试编写 | P0 | 8h | ⬜ |
| 6.3 | 端到端测试 | P0 | 8h | ⬜ |
| 6.4 | 性能优化 (记忆检索) | P1 | 6h | ⬜ |
| 6.5 | 性能优化 (Agent 并发) | P1 | 6h | ⬜ |
| 6.6 | API 文档完善 | P0 | 4h | ⬜ |
| 6.7 | 用户文档编写 | P0 | 6h | ⬜ |
| 6.8 | Docker 镜像优化 | P1 | 4h | ⬜ |

**验收标准**:
- [ ] 核心功能测试覆盖率>80%
- [ ] 端到端流程无阻塞
- [ ] API 文档完整
- [ ] 用户可以独立部署使用

---

## 6. 风险评估

### 6.1 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| LLM API 不稳定 | 中 | 高 | 支持多提供商，自动切换 |
| 向量检索慢 | 中 | 中 | 添加缓存层，优化索引 |
| 记忆膨胀 | 高 | 中 | 定期压缩摘要，归档旧数据 |
| Agent 工作流卡死 | 中 | 高 | 超时机制，自动重试 |
| 知识图谱构建复杂 | 高 | 中 | 先用 NetworkX，后期可换 Neo4j |

### 6.2 项目风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 范围蔓延 | 高 | 高 | 严格按阶段实施，MVP 优先 |
| 时间估算不足 | 中 | 中 | 每阶段预留 20% 缓冲 |
| 学习曲线陡峭 | 中 | 中 | 详细文档，代码注释 |

---

## 7. 验收标准

### 7.1 功能验收

- [ ] **配置管理**: 可以配置火山/阿里云/eggfans API 密钥，测试连接
- [ ] **作品学习**: 可以上传小说，系统自动分析风格并分类到派系
- [ ] **派系管理**: 可以查看派系、检查兼容性、融合派系
- [ ] **写作流程**: 输入大纲，系统自动创作章节并保存
- [ ] **记忆检索**: 写作时自动检索相关记忆，应用学到的技巧
- [ ] **学习闭环**: 章节完成后自动评估，更新风格模型
- [ ] **实时监控**: 前端可以实时查看 Agent 状态和日志
- [ ] **版本控制**: 章节自动 Git 提交，可追溯历史

### 7.2 性能验收

- [ ] 章节生成时间 < 5 分钟 (3000 字)
- [ ] 记忆检索时间 < 2 秒
- [ ] 支持并发 3 个以上写作任务
- [ ] 内存占用 < 2GB (空闲时)

### 7.3 质量验收

- [ ] 核心功能测试覆盖率 > 80%
- [ ] 无阻塞性 bug
- [ ] API 文档完整
- [ ] 用户可以独立部署使用

---

## 附录

### A. API 接口清单

详见 [API 设计文档](./api-design.md)

### B. 数据库设计

详见 [数据库设计文档](./database-design.md)

### C. Agent Prompt 设计

详见 [Prompt 设计文档](./prompt-design.md)

---

**文档结束**
