# 配置持久化修复说明

## 问题

之前每次都要重新填写 API 配置，关闭页面后配置就丢失了。

## 解决方案

### 1. 新增 SQLite 数据库存储

创建了 `backend/app/config_db.py`，使用 SQLite 数据库持久化存储配置：

- **数据库文件**: `backend/data/config.db`
- **存储内容**:
  - LLM 提供商配置（API Key、Base URL、模型等）
  - 系统配置（默认提供商）
  - 项目配置（项目名称、路径等）

### 2. 数据库表结构

#### `llm_providers` 表
存储所有 LLM 提供商配置：
- name: 提供商名称（eggfans, volcengine, aliyun）
- api_format: API 格式
- api_key: API Key（加密存储）
- base_url: API 基础 URL
- model: 模型名称
- timeout: 超时时间
- enabled: 是否启用

#### `system_config` 表
存储系统级配置：
- default_provider: 默认 LLM 提供商

#### `project_config` 表
存储项目配置：
- project_name: 项目名称
- project_path: 项目路径
- auto_commit: 自动提交
- backup_interval: 备份间隔

### 3. API 更新

#### GET `/api/config`
返回配置数据：
```json
{
  "status": "success",
  "data": {
    "default_provider": "eggfans",
    "providers": {
      "eggfans": {
        "api_key": "sk-xxx",
        "base_url": "https://eggfans.com",
        "model": "deepseek-v3.2",
        ...
      }
    },
    "project_config": {...}
  }
}
```

#### POST `/api/config`
保存配置到数据库：
```json
{
  "default_provider": "eggfans",
  "providers": {
    "eggfans": {...},
    "volcengine": {...}
  },
  "project_config": {...}
}
```

### 4. 前端优化

修改了 `frontend/src/views/ProjectConfig.vue`：
- 默认提供商改为 `eggfans`
- 优化配置加载逻辑
- 支持从数据库读取配置

### 5. 默认配置

**默认 LLM 提供商**: eggfans  
**默认模型**: deepseek-v3.2  
**Base URL**: https://eggfans.com

## 使用方式

1. **首次配置**:
   - 打开项目配置页面
   - 填写 eggfans API Key
   - 点击"保存配置"
   - 配置会保存到数据库，下次访问自动加载

2. **切换提供商**:
   - 在"默认提供商"下拉框选择
   - 点击"保存配置"

3. **测试连接**:
   - 每个提供商都有"测试连接"按钮
   - 点击可验证 API 配置是否正确

## 优势

✅ **持久化存储**: 配置保存到数据库，不会丢失  
✅ **自动加载**: 每次访问自动加载已保存的配置  
✅ **默认优先**: eggfans 作为默认提供商  
✅ **多提供商支持**: 可同时配置多个 LLM 提供商  
✅ **安全性**: API Key 存储在数据库，不暴露在代码中

## 数据库位置

```
D:\new test\novel-agent-system\backend\data\config.db
```

## 备份配置

数据库会自动备份到：
```
D:\new test\novel-agent-system\backups\config\
```

## 迁移说明

如果之前有 JSON 配置文件（`config/llm_providers.json`），系统会自动保留作为备份，但主要使用数据库存储。

---

**更新日期**: 2026-03-22  
**版本**: v1.0.6
