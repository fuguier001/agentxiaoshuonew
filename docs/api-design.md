# API 设计文档

**版本**: v1.0  
**最后更新**: 2026-03-21

---

## 📋 目录

1. [API 概览](#1-api-概览)
2. [配置管理](#2-配置管理)
3. [Agent 管理](#3-agent-管理)
4. [写作流程](#4-写作流程)
5. [学习系统](#5-学习系统)
6. [派系管理](#6-派系管理)
7. [健康检查](#7-健康检查)
8. [错误码](#8-错误码)

---

## 1. API 概览

### 1.1 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (可选，默认关闭)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 通用响应格式

**成功响应**:
```json
{
  "status": "success",
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**:
```json
{
  "status": "error",
  "error": "ErrorType",
  "code": "ERROR_CODE",
  "message": "错误描述",
  "details": { ... }
}
```

### 1.3 通用状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源未找到 |
| 429 | 请求过多 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 2. 配置管理

### 2.1 获取配置

```http
GET /api/config
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "app": {
      "project_name": "我的小说",
      "project_path": "./projects/我的小说",
      "default_provider": "volcengine"
    },
    "llm_providers": {
      "volcengine": {
        "api_format": "openai",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-pro-32k",
        "api_key": "***xxxx"
      }
    },
    "memory": {
      "vector_db_path": "./data/vector_db",
      "graph_db_type": "networkx"
    }
  }
}
```

### 2.2 更新配置

```http
POST /api/config
Content-Type: application/json

{
  "project_name": "新小说",
  "default_provider": "aliyun"
}
```

### 2.3 测试 LLM 连接

```http
POST /api/llm/test
Content-Type: application/json

{
  "provider": "volcengine"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "provider": "volcengine",
    "connected": true,
    "response_time_ms": 234,
    "sample_response": "Hello! How can I help you?"
  }
}
```

### 2.4 验证配置

```http
POST /api/llm/validate
Content-Type: application/json

{
  "provider": "volcengine",
  "api_key": "sk-xxx",
  "base_url": "https://...",
  "model": "..."
}
```

---

## 3. Agent 管理

### 3.1 获取所有 Agent 状态

```http
GET /api/agents/status
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "agents": [
      {
        "agent_id": "editor_agent",
        "state": "idle",
        "last_active": "2026-03-21T18:00:00",
        "config": { ... }
      },
      {
        "agent_id": "writer_agent",
        "state": "working",
        "last_active": "2026-03-21T18:05:00",
        "current_task": "write_chapter"
      }
    ]
  }
}
```

### 3.2 执行 Agent 任务

```http
POST /api/agents/{agent_id}/execute
Content-Type: application/json

{
  "action": "analyze_external_work",
  "author": "金庸",
  "title": "天龙八部",
  "text": "..."
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "task_id": "task_123456",
    "agent_id": "learning_agent",
    "status": "started",
    "estimated_time_seconds": 60
  }
}
```

### 3.3 查询任务状态

```http
GET /api/tasks/{task_id}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "task_id": "task_123456",
    "status": "completed",
    "progress": 100,
    "result": { ... },
    "started_at": "2026-03-21T18:00:00",
    "completed_at": "2026-03-21T18:01:00"
  }
}
```

---

## 4. 写作流程

### 4.1 创建章节任务

```http
POST /api/writing/chapter
Content-Type: application/json

{
  "project_id": "project_001",
  "chapter_num": 5,
  "outline": "主角首次遭遇反派，展现两人性格对比",
  "style_id": "style_fused_001",
  "word_count_target": 3000
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "workflow_id": "workflow_789",
    "chapter_num": 5,
    "status": "started",
    "stages": [
      {"name": "plot_refine", "status": "pending"},
      {"name": "character_prep", "status": "pending"},
      {"name": "writing", "status": "pending"},
      {"name": "dialogue_polish", "status": "pending"},
      {"name": "review", "status": "pending"},
      {"name": "final_edit", "status": "pending"}
    ]
  }
}
```

### 4.2 查询工作流状态

```http
GET /api/writing/workflow/{workflow_id}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "workflow_id": "workflow_789",
    "status": "in_progress",
    "progress": 60,
    "current_stage": "dialogue_polish",
    "completed_stages": ["plot_refine", "character_prep", "writing"],
    "result": {
      "draft_content": "..."
    }
  }
}
```

### 4.3 获取章节内容

```http
GET /api/writing/chapter/{project_id}/{chapter_num}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "chapter_num": 5,
    "title": "初遇反派",
    "content": "...",
    "word_count": 3245,
    "created_at": "2026-03-21T18:00:00",
    "revisions": [
      {"version": 1, "created_at": "..."},
      {"version": 2, "created_at": "..."}
    ]
  }
}
```

### 4.4 更新章节

```http
PUT /api/writing/chapter/{project_id}/{chapter_num}
Content-Type: application/json

{
  "content": "修改后的内容...",
  "revision_note": "修改对话节奏"
}
```

---

## 5. 学习系统

### 5.1 上传作品分析

```http
POST /api/learning/analyze
Content-Type: application/json

{
  "author": "金庸",
  "title": "天龙八部",
  "text": "小说内容...",
  "chapters": ["第 1 章", "第 2 章", "..."]
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_001",
    "work": "金庸 - 天龙八部",
    "status": "processing",
    "estimated_time_minutes": 10
  }
}
```

### 5.2 查询分析进度

```http
GET /api/learning/analysis/{analysis_id}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_001",
    "status": "completed",
    "progress": 100,
    "result": {
      "style_id": "style_wuxia_jinyong",
      "school": "wuxia_jinyong",
      "features": [...],
      "techniques": [...]
    }
  }
}
```

### 5.3 获取已分析作品列表

```http
GET /api/learning/works
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "works": [
      {
        "analysis_id": "analysis_001",
        "author": "金庸",
        "title": "天龙八部",
        "analyzed_at": "2026-03-21T18:00:00",
        "style_id": "style_wuxia_jinyong",
        "chapter_count": 50
      }
    ]
  }
}
```

### 5.4 获取作品详细分析

```http
GET /api/learning/works/{analysis_id}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "author": "金庸",
    "title": "天龙八部",
    "analysis": {
      "narrative_style": "多线叙事，历史背景厚重",
      "dialogue_style": "半文半白，富有哲理",
      "description_style": "武功描写细致，场景宏大",
      "emotional_style": "家国情怀浓厚"
    },
    "extracted_techniques": [
      {
        "name": "多线交织",
        "category": "structure",
        "description": "..."
      }
    ],
    "style_dimensions": {
      "narrative_pace": 5,
      "description_density": 8,
      "dialogue_ratio": 6,
      "emotional_intensity": 7
    }
  }
}
```

### 5.5 获取学习报告

```http
GET /api/learning/report?project_id=project_001
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "project_id": "project_001",
    "analyzed_works": 3,
    "style_features_learned": 15,
    "chapters_evaluated": 10,
    "average_score": 7.5,
    "style_evolution": {
      "trend": "improving",
      "score_change": "+0.5"
    },
    "recommendations": [
      "加强对话个性化",
      "增加场景描写细节",
      "控制叙事节奏"
    ]
  }
}
```

---

## 6. 派系管理

### 6.1 获取派系列表

```http
GET /api/schools?category=wuxia
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "schools": [
      {
        "school_id": "wuxia_jinyong",
        "name": "金庸派",
        "category": "wuxia",
        "description": "厚重历史感，家国情怀",
        "key_features": ["历史背景厚重", "多线叙事"],
        "member_count": 5
      }
    ]
  }
}
```

### 6.2 获取派系详情

```http
GET /api/schools/{school_id}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "school_id": "wuxia_jinyong",
    "name": "金庸派",
    "category": "wuxia",
    "description": "...",
    "key_features": [...],
    "style_dimensions": {
      "narrative_pace": 5,
      "description_density": 8
    },
    "representative_works": ["射雕英雄传", "天龙八部"],
    "compatible_schools": ["wuxia_gulong"],
    "incompatible_schools": ["romance_qiongyao"]
  }
}
```

### 6.3 检查派系兼容性

```http
POST /api/schools/check-fusion
Content-Type: application/json

{
  "school_ids": ["wuxia_jinyong", "wuxia_gulong"]
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "compatible": true,
    "score": 0.85,
    "conflicts": [],
    "suggestions": [
      "两个派系都属于武侠类，兼容性好",
      "可以融合出'历史悬疑武侠'风格"
    ]
  }
}
```

### 6.4 融合派系

```http
POST /api/schools/fuse
Content-Type: application/json

{
  "school_ids": ["wuxia_jinyong", "wuxia_gulong"],
  "fusion_name": "历史悬疑武侠",
  "weights": {
    "wuxia_jinyong": 0.6,
    "wuxia_gulong": 0.4
  }
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "style_id": "fused_style_001",
    "style_name": "历史悬疑武侠",
    "source_schools": ["wuxia_jinyong", "wuxia_gulong"],
    "compatibility_score": 0.85,
    "created_at": "2026-03-21T18:00:00"
  }
}
```

### 6.5 应用风格

```http
POST /api/schools/apply-style
Content-Type: application/json

{
  "style_id": "fused_style_001"
}
```

---

## 7. 健康检查

### 7.1 完整健康检查

```http
GET /api/health?detailed=true
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-21T18:00:00",
  "checks": {
    "database": {"status": "ok"},
    "vector_db": {"status": "ok"},
    "llm_providers": [
      {"provider": "volcengine", "status": "ok"},
      {"provider": "aliyun", "status": "ok"}
    ],
    "redis": {"status": "ok"},
    "celery": {"status": "ok", "workers": 4},
    "disk_space": {"status": "ok", "free_gb": 100},
    "memory": {"status": "ok", "memory_percent": 45},
    "agents": [
      {"agent_id": "editor_agent", "status": "ok", "state": "idle"}
    ]
  },
  "summary": {
    "total_checks": 10,
    "healthy": 10,
    "warnings": 0,
    "errors": 0
  }
}
```

### 7.2 就绪检查

```http
GET /api/health/ready
```

### 7.3 存活检查

```http
GET /api/health/live
```

### 7.4 性能指标

```http
GET /api/health/metrics
```

---

## 8. 错误码

### 8.1 LLM 相关

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-----------|
| LLM_PROVIDER_ERROR | LLM 提供商错误 | 500 |
| LLM_RATE_LIMIT | 速率限制 | 429 |
| LLM_TIMEOUT | 调用超时 | 504 |
| LLM_CONFIG_ERROR | 配置错误 | 400 |

### 8.2 记忆系统

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-----------|
| MEMORY_ERROR | 记忆系统错误 | 500 |
| VECTOR_STORE_ERROR | 向量数据库错误 | 500 |
| MEMORY_NOT_FOUND | 记忆未找到 | 404 |

### 8.3 Agent 相关

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-----------|
| AGENT_EXECUTION_ERROR | Agent 执行错误 | 500 |
| AGENT_TIMEOUT | Agent 超时 | 504 |
| AGENT_NOT_REGISTERED | Agent 未注册 | 404 |

### 8.4 派系系统

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-----------|
| SCHOOL_FUSION_ERROR | 派系融合错误 | 400 |
| SCHOOL_INCOMPATIBLE | 派系不兼容 | 400 |
| SCHOOL_NOT_FOUND | 派系未找到 | 404 |

### 8.5 通用错误

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-----------|
| VALIDATION_ERROR | 验证失败 | 400 |
| NOT_FOUND | 资源未找到 | 404 |
| INTERNAL_ERROR | 内部错误 | 500 |
| UNAUTHORIZED | 未授权 | 401 |
| FORBIDDEN | 禁止访问 | 403 |

---

**文档结束**
