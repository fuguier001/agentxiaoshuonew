from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Any, Dict
import logging
import asyncio
import json

from app.api.responses import error_response, success_response
from app.services.auto_service import get_auto_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["全自动创作"])

# 全局进度存储
_progress_store: Dict[str, Dict[str, Any]] = {}


def update_progress(title: str, step: int, step_name: str, status: str, message: str = "", data: Dict = None):
    """更新进度（供其他模块调用）"""
    global _progress_store
    _progress_store[title] = {
        "step": step,
        "step_name": step_name,
        "status": status,
        "message": message,
        "data": data or {},
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    logger.info(f"[进度更新] {title}: Step {step} - {step_name} - {status} - {message}")


@router.get("/auto/progress/{title}")
async def get_progress(title: str):
    """获取当前进度（轮询方式）"""
    global _progress_store
    progress = _progress_store.get(title, {"status": "not_started", "message": "未开始"})
    return success_response(progress)


@router.get("/auto/progress-stream/{title}")
async def progress_stream(title: str):
    """SSE 实时进度推送"""
    async def event_generator():
        last_step = -1
        no_update_count = 0

        while True:
            progress = _progress_store.get(title, {"status": "not_started", "step": -1})

            # 只有当进度变化时才发送
            current_step = progress.get("step", -1)
            if current_step != last_step or progress.get("status") in ["completed", "error"]:
                yield f"data: {json.dumps(progress, ensure_ascii=False)}\n\n"
                last_step = current_step
                no_update_count = 0

                # 如果完成或出错，结束流
                if progress.get("status") in ["completed", "error"]:
                    break
            else:
                no_update_count += 1

            await asyncio.sleep(0.5)

            # 超时检查（5分钟无更新则结束）
            if no_update_count > 600:
                yield f"data: {json.dumps({'status': 'timeout', 'message': '等待超时'})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/auto/create")
async def auto_create_novel(data: Dict[str, Any]):
    try:
        title = data.get("title", "")
        resume = data.get("resume", True)  # 默认启用断点续传

        # 更新 Agent 状态为工作中
        from app.agents.registry import update_agent_status
        update_agent_status("writer_agent", "running", f"正在创作《{title}》")

        # 初始化进度
        update_progress(title, 0, "init", "starting", "开始创作...")

        result = await get_auto_service().create_novel(data, resume=resume)
        if result.get("status") == "success":
            update_progress(title, 5, "completed", "completed", "创作完成！", {
                "novel_id": result["novel_id"]
            })
            # 更新 Agent 状态为空闲
            update_agent_status("writer_agent", "idle", "创作完成")
            return success_response({
                "novel_id": result["novel_id"],
                "blueprint": result["blueprint"],
                "first_chapter": result["first_chapter"]
            }, f"小说《{title}》创作完成！已生成世界观、3000 章规划和第一章")
        # 检查是否是断点保存的错误
        if result.get("checkpoint_saved"):
            update_progress(title, result.get("resume_from_step", 0), "paused", "paused", "创作中断，已保存断点")
            update_agent_status("writer_agent", "idle", "创作中断")
            return error_response(
                result.get("error", "创作中断"),
                code="CHECKPOINT_SAVED",
                details={
                    "resume_from_step": result.get("resume_from_step"),
                    "partial_data": result.get("partial_data", {})
                },
                status_code=202  # Accepted - 部分完成
            )

        update_progress(title, -1, "error", "error", result.get("error", "创作失败"))
        update_agent_status("writer_agent", "idle", "创作失败")
        return error_response(result.get("error", "创作失败"), code="AUTO_CREATE_FAILED", details=result, status_code=400)
    except ValueError as e:
        update_progress(title, -1, "error", "error", str(e))
        update_agent_status("writer_agent", "idle", "创作失败")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"全自动创作失败：{e}")
        update_progress(title, -1, "error", "error", str(e))
        update_agent_status("writer_agent", "idle", "创作失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto/checkpoint/{title}")
async def get_checkpoint_status(title: str):
    """获取断点续传状态"""
    try:
        from app.novel_architect import get_auto_creation_system

        system = get_auto_creation_system()
        status = system.architect.get_checkpoint_status(title)

        return success_response(status)
    except Exception as e:
        logger.error(f"获取断点状态失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/auto/checkpoint/{title}")
async def delete_checkpoint(title: str):
    """删除断点"""
    try:
        from app.novel_architect import get_auto_creation_system

        system = get_auto_creation_system()
        system.architect.delete_checkpoint(title)

        return success_response({"deleted": True}, "断点已删除")
    except Exception as e:
        logger.error(f"删除断点失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto/blueprint/{novel_id}")
async def get_novel_blueprint(novel_id: str):
    try:
        result = get_auto_service().get_blueprint(novel_id)
        if not result:
            raise HTTPException(status_code=404, detail="小说不存在")
        return success_response(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取蓝图失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
