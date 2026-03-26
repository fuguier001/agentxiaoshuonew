# 当前工程状态说明

本文档用于快速说明这个仓库当前“已经完成到哪一步”，帮助后续继续开发、协作或交接。

## 目前已经完成的关键工程收口

### 1. 配置统一

- 运行时配置以 SQLite 为真源
- 通过 `backend/app/services/config_service.py` 统一读写
- `/api/config` 不返回明文 API Key
- health / LLM test / workflow 已对齐统一配置路径

### 2. 章节存储统一

- 章节数据已统一到数据库真源
- `writing` 和 `novels` 接口共享同一份章节数据
- `chapter_service.py` 承担章节保存与读取的主逻辑

### 3. 前端导航统一

- 前端已接入 `vue-router`
- `App.vue` 已切换为 `router-view`
- 已移除关键页面中的 `window.location.href` 导航方式

### 4. 后端 API 模块化

旧的 `backend/app/api/routes.py` 已删除。

当前 API 已拆成：

- `novel_routes.py`
- `config_routes.py`
- `writing_routes.py`
- `learning_routes.py`
- `agent_routes.py`
- `ai_routes.py`
- `auto_routes.py`
- `school_routes.py`
- `health.py`

### 5. service 层已初步建立

当前已存在：

- `config_service.py`
- `chapter_service.py`
- `novel_service.py`
- `writing_service.py`
- `learning_service.py`
- `agent_service.py`
- `ai_service.py`
- `auto_service.py`
- `school_service.py`

这些 service 已开始承载核心业务逻辑，route 层明显变薄。

### 6. API 响应结构已统一

- 已新增 `backend/app/api/responses.py`
- 成功响应统一包含：`success / status / data`
- 错误响应统一包含：`success / status / error.code / error.message`

### 7. 前端构建已优化一轮

- 路由已切换为懒加载
- Vite 已配置基础 `manualChunks`
- 主包已从单一大包拆成多 chunk，但 `elementPlus` 包仍然偏大

### 8. Docker 交付链路补齐一部分

- 已补充 `frontend/Dockerfile`
- `docker-compose.yml` 的前端服务不再是缺少构建文件的状态

### 9. CI 基线已建立

- 已新增 `.github/workflows/ci.yml`
- 后端会运行核心 pytest 回归测试
- 前端会执行生产构建验证

## 当前仍然建议继续处理的事项

### 高优先级

1. 继续收口更多细节接口到统一 response schema（尤其 health / 边缘接口）
2. 更新并收敛 Docker 运行链路
3. 进一步压缩前端构建产物

### 中优先级

1. 梳理 FastAPI / Starlette 在 Python 3.14 下的 warning
2. 给前端加入更系统的测试与契约校验
3. 增加 CI / 自动化验证

## 当前推荐开发方式

### 本地开发优先

后端：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 不建议当前阶段优先依赖

- Docker 全量生产链路
- Celery 作为唯一运行路径

当前更适合：

- 本地后端 + 本地前端
- pytest 回归验证
- 逐步重构

## 当前验证基线

最近已验证通过的测试包括：

- `test_config_service.py`
- `test_config_api.py`
- `test_chapter_storage.py`
- `test_route_registration.py`
- `test_service_routes.py`
- `test_response_schema.py`
- `test_extended_services.py`

建议持续使用：

```bash
python -m pytest backend/tests/test_config_service.py backend/tests/test_config_api.py backend/tests/test_chapter_storage.py backend/tests/test_route_registration.py backend/tests/test_service_routes.py backend/tests/test_response_schema.py backend/tests/test_extended_services.py -v
```

## 一句话总结

这个项目已经从“功能原型混合态”进入“结构完整、具备持续优化条件的工程化状态”，距离最终稳定版还差依赖治理、性能优化与部署收尾。
