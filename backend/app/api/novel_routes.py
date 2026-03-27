from fastapi import APIRouter
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, field_validator
import logging
import asyncio
import uuid
from datetime import datetime
from collections import deque

from app.services.chapter_service import get_chapter_service
from app.services.novel_service import get_novel_service
from app.api.responses import success_response, error_response
from app.workflow_executor import get_workflow_executor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["小说管理"])


# ========== Pydantic 模型验证 ==========

class BlueprintUpdateRequest(BaseModel):
    """蓝图更新请求验证"""
    world_map: Optional[Dict[str, Any]] = Field(default=None, max_length=50000)
    macro_plot: Optional[Dict[str, Any]] = Field(default=None, max_length=50000)
    character_system: Optional[Dict[str, Any]] = Field(default=None, max_length=50000)
    hook_network: Optional[Dict[str, Any]] = Field(default=None, max_length=50000)

    @field_validator('world_map', 'macro_plot', 'character_system', 'hook_network')
    @classmethod
    def validate_dict_depth(cls, v):
        """验证字典嵌套深度不超过 5 层"""
        if v is None:
            return v

        def get_depth(d, current=0):
            if not isinstance(d, dict) or not d:
                return current
            return max(get_depth(val, current + 1) for val in d.values() if isinstance(val, dict))

        depth = get_depth(v)
        if depth > 5:
            raise ValueError('JSON 嵌套深度不能超过 5 层')
        return v


class BlueprintPolishRequest(BaseModel):
    """蓝图润色请求验证"""
    type: str = Field(..., pattern="^(current|all)$", description="润色类型：current 或 all")
    field: str = Field(default="world_map", description="当前润色的字段")
    content: str = Field(default="{}", max_length=100000, description="要润色的内容")
    requirement: str = Field(..., min_length=1, max_length=2000, description="润色要求")

    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        """验证字段名"""
        allowed_fields = ['world_map', 'macro_plot', 'character_system', 'hook_network']
        if v not in allowed_fields:
            raise ValueError(f'field 必须是: {", ".join(allowed_fields)}')
        return v


class ChapterRewriteRequest(BaseModel):
    """章节重写请求验证"""
    requirement: Optional[str] = Field(default="", max_length=1000, description="重写要求")

# ========== 任务队列系统（串行执行，避免并发） ==========
class TaskQueue:
    """串行任务队列 - 一次只执行一个任务"""

    # 任务过期时间（秒）
    TASK_EXPIRY_SECONDS = 3600  # 1小时后自动清理

    def __init__(self):
        self.queue: deque = deque()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.is_processing = False
        self._lock = asyncio.Lock()

    def _cleanup_expired_tasks(self):
        """清理过期任务（1小时前完成的）"""
        now = datetime.now()
        expired_ids = []

        for task_id, task in self.tasks.items():
            if task.get("status") in ["completed", "failed"]:
                completed_at = task.get("completed_at")
                if completed_at:
                    try:
                        completed_time = datetime.fromisoformat(completed_at)
                        if (now - completed_time).total_seconds() > self.TASK_EXPIRY_SECONDS:
                            expired_ids.append(task_id)
                    except:
                        pass

        for task_id in expired_ids:
            del self.tasks[task_id]
            logger.info(f"清理过期任务: {task_id}")

        if expired_ids:
            logger.info(f"已清理 {len(expired_ids)} 个过期任务")

    def add_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """添加任务到队列"""
        # 先清理过期任务
        self._cleanup_expired_tasks()

        task_id = f"{task_type}_{task_data.get('novel_id', '')}_{task_data.get('chapter_num', 0)}_{uuid.uuid4().hex[:8]}"

        task = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "queued",
            "progress": 0,
            "current_step": "排队中",
            "queue_position": len(self.queue) + 1,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            **task_data
        }

        self.tasks[task_id] = task
        self.queue.append(task_id)
        logger.info(f"任务加入队列: {task_id}, 队列位置: {task['queue_position']}")

        # 尝试处理队列
        asyncio.create_task(self._process_queue())

        return task_id

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        return self.tasks.get(task_id)

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "queue_length": len(self.queue),
            "is_processing": self.is_processing,
            "pending_tasks": list(self.queue)
        }

    def update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)

    async def _process_queue(self):
        """处理队列中的任务（串行）"""
        async with self._lock:
            if self.is_processing:
                return

            while self.queue:
                self.is_processing = True
                task_id = self.queue.popleft()

                # 更新队列位置
                for i, tid in enumerate(self.queue):
                    self.tasks[tid]["queue_position"] = i + 1

                task = self.tasks.get(task_id)
                if not task:
                    continue

                try:
                    logger.info(f"开始执行任务: {task_id}")
                    self.update_task(task_id, status="running", started_at=datetime.now().isoformat())

                    # 根据任务类型执行
                    if task["task_type"] == "rewrite":
                        await self._execute_rewrite_task(task_id, task)
                    elif task["task_type"] == "continue":
                        await self._execute_continue_task(task_id, task)

                    logger.info(f"任务完成: {task_id}")

                except Exception as e:
                    logger.error(f"任务执行失败: {task_id}, 错误: {e}")
                    self.update_task(task_id, status="failed", error=str(e), completed_at=datetime.now().isoformat())

                finally:
                    self.is_processing = False

    async def _execute_rewrite_task(self, task_id: str, task: Dict[str, Any]):
        """执行重写任务"""
        try:
            executor = get_workflow_executor()

            # 更新进度
            steps = [
                ("剧情架构师 - 细化大纲", 15),
                ("人物设计师 - 准备角色", 30),
                ("章节写手 - 撰写初稿", 50),
                ("对话专家 - 打磨对话", 65),
                ("审核编辑 - 质量把控", 80),
                ("主编 - 最终审核", 95)
            ]

            for i, (step_name, progress) in enumerate(steps):
                self.update_task(task_id, progress=progress, current_step=step_name)

            result = await executor.execute_chapter_workflow(
                novel_id=task["novel_id"],
                chapter_num=task["chapter_num"],
                outline=task.get("outline", ""),
                word_count_target=3000,
                style='default'
            )

            if result.get('status') == 'success':
                content = result.get('content', '')

                # 保存章节
                get_chapter_service().save_chapter(
                    novel_id=task["novel_id"],
                    chapter_num=task["chapter_num"],
                    content=content,
                    title=task.get("chapter_title", ""),
                    outline=task.get("outline", ""),
                    status='published'
                )

                self.update_task(task_id,
                    status="completed",
                    progress=100,
                    current_step="完成",
                    completed_at=datetime.now().isoformat(),
                    result={
                        "chapter_num": task["chapter_num"],
                        "title": task.get("chapter_title", ""),
                        "word_count": len(content)
                    }
                )
            else:
                self.update_task(task_id,
                    status="failed",
                    error=result.get('message', '重写失败'),
                    completed_at=datetime.now().isoformat()
                )

        except Exception as e:
            logger.error(f"重写任务执行失败: {e}")
            self.update_task(task_id, status="failed", error=str(e), completed_at=datetime.now().isoformat())

    async def _execute_continue_task(self, task_id: str, task: Dict[str, Any]):
        """执行续写任务"""
        try:
            executor = get_workflow_executor()

            steps = [
                ("读取蓝图数据", 10),
                ("生成章节大纲", 20),
                ("撰写初稿", 50),
                ("打磨对话", 70),
                ("审核编辑", 90),
                ("保存章节", 100)
            ]

            for i, (step_name, progress) in enumerate(steps):
                self.update_task(task_id, progress=progress, current_step=step_name)

            result = await executor.execute_chapter_workflow(
                novel_id=task["novel_id"],
                chapter_num=task["chapter_num"],
                outline=task.get("outline", ""),
                word_count_target=3000,
                style='default'
            )

            if result.get('status') == 'success':
                content = result.get('content', '')

                get_chapter_service().save_chapter(
                    novel_id=task["novel_id"],
                    chapter_num=task["chapter_num"],
                    content=content,
                    title=f"第{task['chapter_num']}章",
                    outline=task.get("outline", ""),
                    status='published'
                )

                self.update_task(task_id,
                    status="completed",
                    progress=100,
                    current_step="完成",
                    completed_at=datetime.now().isoformat(),
                    result={
                        "chapter_num": task["chapter_num"],
                        "word_count": len(content)
                    }
                )
            else:
                self.update_task(task_id,
                    status="failed",
                    error=result.get('message', '续写失败'),
                    completed_at=datetime.now().isoformat()
                )

        except Exception as e:
            logger.error(f"续写任务执行失败: {e}")
            self.update_task(task_id, status="failed", error=str(e), completed_at=datetime.now().isoformat())


# 全局任务队列
task_queue = TaskQueue()


@router.get("/novels")
async def list_novels(page: int = 1, page_size: int = 20):
    """获取小说列表（不包括回收站）

    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量（默认 20，最大 100）
    """
    try:
        from app.novel_db import get_novel_database

        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        db = get_novel_database()
        all_novels = db.list_novels()  # 这个方法应该排除 deleted_at 不为空的

        # 分页计算
        total = len(all_novels)
        start = (page - 1) * page_size
        end = start + page_size
        novels = all_novels[start:end]

        return success_response({
            "novels": novels,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        })
    except Exception as e:
        logger.error(f"获取小说列表失败：{e}")
        return error_response(str(e), code="LIST_NOVELS_FAILED", status_code=500)


@router.post("/novels")
async def create_novel(novel_data: Dict[str, Any]):
    try:
        result = get_novel_service().create_novel(novel_data)
        return success_response(result, "小说创建成功")
    except ValueError as e:
        return error_response(str(e), code="INVALID_INPUT", status_code=400)
    except Exception as e:
        logger.error(f"创建小说失败：{e}")
        return error_response(str(e), code="CREATE_NOVEL_FAILED", status_code=500)


@router.get("/novels/{novel_id}")
async def get_novel(novel_id: str):
    try:
        novel = get_novel_service().get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)
        return success_response(novel)
    except Exception as e:
        logger.error(f"获取小说详情失败：{e}")
        return error_response(str(e), code="GET_NOVEL_FAILED", status_code=500)


@router.put("/novels/{novel_id}")
async def update_novel(novel_id: str, novel_data: Dict[str, Any]):
    try:
        if not get_novel_service().update_novel(novel_id, novel_data):
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)
        return success_response(None, "小说已更新")
    except Exception as e:
        logger.error(f"更新小说失败：{e}")
        return error_response(str(e), code="UPDATE_NOVEL_FAILED", status_code=500)


@router.delete("/novels/{novel_id}")
async def delete_novel(novel_id: str):
    """删除小说（移动到回收站）"""
    try:
        from app.novel_db import get_novel_database
        db = get_novel_database()
        if db.soft_delete_novel(novel_id):
            return success_response(None, "小说已移至回收站")
        else:
            return error_response("小说不存在或已在回收站", code="NOVEL_NOT_FOUND", status_code=404)
    except Exception as e:
        logger.error(f"删除小说失败：{e}")
        return error_response(str(e), code="DELETE_NOVEL_FAILED", status_code=500)


# ========== 回收站 API ==========

@router.get("/trash")
async def list_trash():
    """获取回收站小说列表"""
    try:
        from app.novel_db import get_novel_database
        db = get_novel_database()
        novels = db.get_trash_novels()
        return success_response({"novels": novels, "total": len(novels)})
    except Exception as e:
        logger.error(f"获取回收站列表失败：{e}")
        return error_response(str(e), code="LIST_TRASH_FAILED", status_code=500)


@router.post("/trash/{novel_id}/restore")
async def restore_novel(novel_id: str):
    """从回收站恢复小说"""
    try:
        from app.novel_db import get_novel_database
        db = get_novel_database()
        if db.restore_novel(novel_id):
            return success_response(None, "小说已恢复")
        else:
            return error_response("小说不在回收站中", code="NOVEL_NOT_IN_TRASH", status_code=404)
    except Exception as e:
        logger.error(f"恢复小说失败：{e}")
        return error_response(str(e), code="RESTORE_NOVEL_FAILED", status_code=500)


@router.delete("/trash/{novel_id}")
async def permanent_delete_novel(novel_id: str):
    """永久删除小说（从数据库彻底删除）"""
    try:
        from app.novel_db import get_novel_database
        db = get_novel_database()
        if db.permanent_delete_novel(novel_id):
            return success_response(None, "小说已永久删除")
        else:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)
    except Exception as e:
        logger.error(f"永久删除小说失败：{e}")
        return error_response(str(e), code="DELETE_PERMANENT_FAILED", status_code=500)


@router.get("/novels/{novel_id}/chapters")
async def list_chapters(novel_id: str, page: int = 1, page_size: int = 50):
    """获取小说章节列表

    Args:
        novel_id: 小说 ID
        page: 页码（从 1 开始）
        page_size: 每页数量（默认 50，最大 200）
    """
    try:
        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50
        if page_size > 200:
            page_size = 200

        all_chapters = get_chapter_service().list_chapters(novel_id)

        # 分页计算
        total = len(all_chapters)
        start = (page - 1) * page_size
        end = start + page_size
        chapters = all_chapters[start:end]

        return success_response({
            "chapters": chapters,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        })
    except Exception as e:
        logger.error(f"获取章节列表失败：{e}")
        return error_response(str(e), code="LIST_CHAPTERS_FAILED", status_code=500)


@router.post("/novels/{novel_id}/chapters")
async def create_chapter(novel_id: str, chapter_data: Dict[str, Any]):
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()
        if not db.get_novel(novel_id):
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        chapter_num = chapter_data.get("chapter_num", 1)
        title = chapter_data.get("title", "")
        outline = chapter_data.get("outline", "")
        chapter_id = get_chapter_service().create_chapter(novel_id, chapter_num, title, outline)
        return success_response({"chapter_id": chapter_id, "chapter_num": chapter_num}, "章节创建成功")
    except Exception as e:
        logger.error(f"创建章节失败：{e}")
        return error_response(str(e), code="CREATE_CHAPTER_FAILED", status_code=500)


@router.get("/novels/{novel_id}/chapters/{chapter_num}")
async def get_chapter(novel_id: str, chapter_num: int):
    try:
        chapter = get_chapter_service().get_chapter(novel_id, chapter_num)
        if not chapter:
            return error_response("章节不存在", code="CHAPTER_NOT_FOUND", status_code=404)
        return success_response(chapter)
    except Exception as e:
        logger.error(f"获取章节失败：{e}")
        return error_response(str(e), code="GET_CHAPTER_FAILED", status_code=500)


@router.put("/novels/{novel_id}/chapters/{chapter_num}")
async def update_chapter(novel_id: str, chapter_num: int, chapter_data: Dict[str, Any]):
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()
        if not db.get_novel(novel_id):
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)
        chapter = get_chapter_service().save_chapter(
            novel_id=novel_id,
            chapter_num=chapter_num,
            content=chapter_data.get("content", ""),
            title=chapter_data.get("title", ""),
            outline=chapter_data.get("outline", ""),
            status=chapter_data.get("status", "draft"),
        )
        return success_response(chapter, "章节已更新")
    except Exception as e:
        logger.error(f"更新章节失败：{e}")
        return error_response(str(e), code="UPDATE_CHAPTER_FAILED", status_code=500)


@router.get("/novels/{novel_id}/characters")
async def list_characters(novel_id: str):
    try:
        characters = get_novel_service().list_characters(novel_id)
        return success_response({"characters": characters, "total": len(characters)})
    except Exception as e:
        logger.error(f"获取人物列表失败：{e}")
        return error_response(str(e), code="LIST_CHARACTERS_FAILED", status_code=500)


@router.post("/novels/{novel_id}/characters")
async def add_character(novel_id: str, character_data: Dict[str, Any]):
    try:
        result = get_novel_service().add_character(novel_id, character_data)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), code="INVALID_INPUT", status_code=400)
    except Exception as e:
        logger.error(f"添加人物失败：{e}")
        return error_response(str(e), code="ADD_CHARACTER_FAILED", status_code=500)


@router.get("/novels/{novel_id}/hooks")
async def list_hooks(novel_id: str):
    try:
        hooks = get_novel_service().list_hooks(novel_id)
        return success_response({"hooks": hooks, "total": len(hooks)})
    except Exception as e:
        logger.error(f"获取伏笔列表失败：{e}")
        return error_response(str(e), code="LIST_HOOKS_FAILED", status_code=500)


# ========== 任务队列 API（串行执行，避免并发） ==========

@router.post("/novels/{novel_id}/chapters/{chapter_num}/rewrite")
async def rewrite_chapter(novel_id: str, chapter_num: int):
    """重写指定章节 - 加入任务队列，串行执行"""
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()

        # 检查小说是否存在
        novel = db.get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        # 获取原章节信息
        chapter = get_chapter_service().get_chapter(novel_id, chapter_num)
        if not chapter:
            return error_response("章节不存在", code="CHAPTER_NOT_FOUND", status_code=404)

        # 加入任务队列
        task_id = task_queue.add_task("rewrite", {
            "novel_id": novel_id,
            "chapter_num": chapter_num,
            "outline": chapter.get('outline', chapter.get('content', '')),
            "chapter_title": chapter.get('title', '')
        })

        queue_status = task_queue.get_queue_status()

        return success_response({
            "task_id": task_id,
            "status": "queued",
            "queue_position": task_queue.get_task(task_id).get("queue_position", 0),
            "message": f"重写任务已加入队列，前面还有 {queue_status['queue_length']} 个任务等待"
        })

    except Exception as e:
        logger.error(f"创建重写任务失败：{e}")
        return error_response(str(e), code="CREATE_REWRITE_TASK_FAILED", status_code=500)


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = task_queue.get_task(task_id)
    if not task:
        return error_response("任务不存在", code="TASK_NOT_FOUND", status_code=404)

    return success_response(task)


@router.get("/queue/status")
async def get_queue_status():
    """获取任务队列状态"""
    return success_response(task_queue.get_queue_status())


@router.get("/novels/{novel_id}/tasks")
async def get_novel_tasks(novel_id: str):
    """获取小说的所有任务"""
    all_tasks = [t for t in task_queue.tasks.values() if t.get("novel_id") == novel_id]
    all_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return success_response({"tasks": all_tasks})


# ========== 蓝图 API ==========

@router.get("/novels/{novel_id}/blueprint")
async def get_novel_blueprint(novel_id: str):
    """获取小说的完整蓝图数据"""
    try:
        from app.services.auto_service import get_auto_service

        result = get_auto_service().get_blueprint(novel_id)
        if not result:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        return success_response(result)
    except Exception as e:
        logger.error(f"获取蓝图失败：{e}")
        return error_response(str(e), code="BLUEPRINT_FETCH_FAILED", status_code=500)


@router.put("/novels/{novel_id}/blueprint")
async def update_novel_blueprint(novel_id: str, blueprint_data: BlueprintUpdateRequest):
    """更新小说的蓝图数据"""
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()

        # 检查小说是否存在
        novel = db.get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        # 验证并保存蓝图数据
        settings = {}

        if blueprint_data.world_map is not None:
            settings["world_map"] = blueprint_data.world_map
        if blueprint_data.macro_plot is not None:
            settings["macro_plot"] = blueprint_data.macro_plot
        if blueprint_data.character_system is not None:
            settings["character_system"] = blueprint_data.character_system
        if blueprint_data.hook_network is not None:
            settings["hook_network"] = blueprint_data.hook_network

        if not settings:
            return error_response("没有有效的蓝图数据", code="INVALID_BLUEPRINT", status_code=400)

        # 保存到数据库
        db.update_novel_settings(novel_id, settings)

        logger.info(f"蓝图已更新：{novel_id}")
        return success_response(None, "蓝图已保存")

    except Exception as e:
        logger.error(f"更新蓝图失败：{e}")
        return error_response(str(e), code="BLUEPRINT_UPDATE_FAILED", status_code=500)


@router.post("/novels/{novel_id}/blueprint/polish")
async def polish_novel_blueprint(novel_id: str, polish_request: BlueprintPolishRequest):
    """AI 润色蓝图"""
    try:
        from app.novel_db import get_novel_database
        from app.utils.llm_client import get_llm_client

        db = get_novel_database()

        # 检查小说是否存在
        novel = db.get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        # 从 Pydantic 模型获取参数
        polish_type = polish_request.type
        field = polish_request.field
        content = polish_request.content
        requirement = polish_request.requirement

        # 获取小说信息用于生成
        novel_info = db.get_novel(novel_id)
        novel_title = novel_info.get("title", "未命名小说") if novel_info else "未命名小说"
        novel_genre = novel_info.get("genre", "fantasy") if novel_info else "fantasy"
        novel_desc = novel_info.get("description", "") if novel_info else ""

        # 构建润色提示词
        field_names = {
            "world_map": "世界观设定",
            "macro_plot": "宏观剧情规划",
            "character_system": "人物体系",
            "hook_network": "伏笔网络"
        }

        field_name = field_names.get(field, field)

        # 判断是生成新内容还是润色现有内容
        is_empty = not content or content == "{}" or content == ""

        if is_empty:
            # 生成新内容的提示词
            prompt = f"""你是一位专业的小说设定创作专家。请为以下小说创建{field_name}：

小说标题：{novel_title}
类型：{novel_genre}
简介：{novel_desc}

创作要求：
{requirement}

请创建一个完整的{field_name}，以 JSON 格式返回。要求：
1. 内容丰富、有创意、逻辑自洽
2. 符合小说类型和风格
3. 包含足够的细节和深度

请直接返回 JSON 内容，不要添加任何解释或说明。"""
        else:
            # 润色现有内容的提示词
            prompt = f"""你是一位专业的小说设定润色专家。请根据以下要求优化小说的{field_name}：

当前内容（JSON 格式）：
{content}

润色要求：
{requirement}

请完成以下任务：
1. 保持 JSON 结构不变
2. 根据要求优化内容，使其更加丰富、合理、有吸引力
3. 增加更多细节和创意元素
4. 确保逻辑一致性

请直接返回优化后的 JSON 内容，不要添加任何解释或说明。"""

        # 调用 LLM
        llm = get_llm_client()
        response = await llm.chat(prompt)

        # 清理响应，提取 JSON
        polished_content = response.strip()
        if polished_content.startswith("```"):
            # 移除代码块标记
            lines = polished_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            polished_content = "\n".join(lines)

        logger.info(f"蓝图润色完成：{novel_id} - {field}")

        return success_response({
            "polished_content": polished_content,
            "field": field
        })

    except Exception as e:
        logger.error(f"蓝图润色失败：{e}")
        return error_response(str(e), code="BLUEPRINT_POLISH_FAILED", status_code=500)


# ========== 续写 API ==========

@router.post("/novels/{novel_id}/continue")
async def continue_novel(novel_id: str):
    """续写小说 - 加入任务队列，串行执行"""
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()

        # 检查小说是否存在
        novel = db.get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        # 获取当前章节数
        chapters = get_chapter_service().list_chapters(novel_id)
        next_chapter_num = len(chapters) + 1

        # 获取蓝图数据
        settings = db.get_novel_settings(novel_id)
        macro_plot = settings.get("macro_plot", {})

        if not macro_plot:
            return error_response("小说没有蓝图数据，无法续写", code="NO_BLUEPRINT", status_code=400)

        # 从宏观规划中提取下一章大纲
        chapter_outline = extract_chapter_outline_from_macro(macro_plot, next_chapter_num)

        # 加入任务队列
        task_id = task_queue.add_task("continue", {
            "novel_id": novel_id,
            "chapter_num": next_chapter_num,
            "outline": chapter_outline
        })

        queue_status = task_queue.get_queue_status()

        return success_response({
            "task_id": task_id,
            "chapter_num": next_chapter_num,
            "status": "queued",
            "queue_position": task_queue.get_task(task_id).get("queue_position", 0),
            "message": f"续写任务已加入队列，前面还有 {queue_status['queue_length']} 个任务等待"
        })

    except Exception as e:
        logger.error(f"续写失败：{e}")
        return error_response(str(e), code="CONTINUE_FAILED", status_code=500)


def extract_chapter_outline_from_macro(macro_plot: Dict, chapter_num: int) -> str:
    """从宏观规划中提取章节大纲"""
    volumes = macro_plot.get("volumes", [])

    for vol in volumes:
        vol_start = vol.get("start_chapter", 1)
        vol_end = vol.get("end_chapter", 100)
        if vol_start <= chapter_num <= vol_end:
            chapters = vol.get("chapters", [])
            for ch in chapters:
                if ch.get("chapter_num") == chapter_num:
                    return ch.get("outline", ch.get("title", "续写章节"))
            return f"第{chapter_num}章 - {vol.get('title', '续写')}，{vol.get('outline', '')}"

    return f"第{chapter_num}章 - 继续剧情发展"


# ========== 导出 API ==========

from fastapi.responses import Response
from urllib.parse import quote


@router.get("/novels/{novel_id}/export/txt")
async def export_novel_txt(novel_id: str):
    """导出小说为 TXT 格式"""
    try:
        service = get_novel_service()
        result = service.export_to_txt(novel_id)

        # URL 编码文件名以支持中文
        encoded_filename = quote(result["filename"])

        # 返回 TXT 文件下载
        return Response(
            content=result["content"].encode("utf-8"),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except ValueError as e:
        return error_response(str(e), code="EXPORT_FAILED", status_code=400)
    except Exception as e:
        logger.error(f"导出小说失败：{e}")
        return error_response(str(e), code="EXPORT_FAILED", status_code=500)


@router.get("/novels/{novel_id}/export")
async def get_export_info(novel_id: str):
    """获取导出信息（预览）"""
    try:
        from app.novel_db import get_novel_database

        db = get_novel_database()
        novel = db.get_novel(novel_id)
        if not novel:
            return error_response("小说不存在", code="NOVEL_NOT_FOUND", status_code=404)

        chapters = get_chapter_service().list_chapters(novel_id)
        total_words = sum(len(ch.get("content", "")) for ch in chapters)

        return success_response({
            "novel_id": novel_id,
            "title": novel.get("title", ""),
            "author": novel.get("author", ""),
            "total_chapters": len(chapters),
            "total_words": total_words,
            "export_formats": ["txt"]
        })

    except Exception as e:
        logger.error(f"获取导出信息失败：{e}")
        return error_response(str(e), code="EXPORT_INFO_FAILED", status_code=500)
