# 仓库清理与依赖治理说明

## 本轮已完成

### 已移除的明显残留文件

- `frontend/src/views/NovelLibrary_broken.vue`
- `frontend/src/views/NovelLibrary_test.vue`

这两个文件都属于历史/实验性质文件，不应继续留在主开发路径中。

### 已加入忽略规则

项目根目录 `.gitignore` 已覆盖：

- `frontend/node_modules/`
- `frontend/dist/`
- `logs/`
- `data/`
- `projects/`
- `backups/`
- `.env`
- `backend/.env`
- Python cache / pytest cache / 虚拟环境目录

## 仍需人工确认的事项

### 1. `frontend/node_modules` 目录

当前本地工作区里这个目录仍然存在，但它已经被 `.gitignore` 忽略。

如果它曾经被 Git 跟踪过，建议开发者在本地确认后执行清理：

```bash
git rm -r --cached frontend/node_modules
```

然后重新提交。

> 注意：这里只建议移除版本跟踪，不影响你本地继续开发时使用 `node_modules`。

### 2. 运行时目录

以下目录现在被视为**本地运行产物**，不建议进入版本控制：

- `data/`
- `projects/`
- `logs/`
- `backups/`

如果历史上已经被跟踪，也建议后续做一次统一清理。

## 仍存在的技术债

### 依赖 warning

当前测试仍有一些 warning，主要来自：

- FastAPI / Starlette 在 Python 3.14 下对 `asyncio.iscoroutinefunction` 的兼容提醒

这类 warning 更偏依赖层面，建议后续统一做：

1. 升级 FastAPI / Starlette / 相关依赖
2. 在固定 Python 版本下重新验证

## CI 基线

仓库现已添加基础 CI：

- Python 3.12 上运行后端核心 pytest 回归测试
- Node 20 上运行前端构建

建议将 CI 作为后续继续重构和升级依赖时的最低保障。

### 前端构建体积

前端构建仍提示 chunk 过大，说明还需要做：

- 路由级懒加载
- manualChunks 拆包
- 依赖分包优化

## 建议的下一轮仓库治理动作

1. 清理历史上被跟踪的 `node_modules` / 运行目录
2. 统一 API response schema
3. 处理剩余依赖 warning
4. 为前端加入更细粒度测试与构建约束
