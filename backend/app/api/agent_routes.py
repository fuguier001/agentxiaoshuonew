from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Any, Dict, Optional
import logging

from app.api.responses import success_response
from app.services.agent_service import get_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Agent 管理"])


@router.get("/agents/status")
async def get_agents_status():
    try:
        return success_response(get_agent_service().get_agents_status())
    except Exception as e:
        logger.error(f"获取 Agent 状态失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task: Dict[str, Any]):
    try:
        result = await get_agent_service().execute_agent_task(agent_id, task)
        if not result:
            raise HTTPException(status_code=404, detail=f"Agent 未找到：{agent_id}")
        return success_response(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行 Agent 任务失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = get_agent_service().get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在：{task_id}")
    return success_response(task)


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    try:
        cancelled_id = get_agent_service().cancel_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cancelled_id:
        raise HTTPException(status_code=404, detail=f"任务不存在：{task_id}")
    return success_response(None, f"任务 {cancelled_id} 已取消")


@router.get("/tasks")
async def list_tasks(status: Optional[str] = None, task_type: Optional[str] = None, limit: int = 50):
    return success_response(get_agent_service().list_tasks(status=status, task_type=task_type, limit=limit))


@router.delete("/tasks")
async def clear_completed_tasks():
    get_agent_service().clear_completed_tasks()
    return success_response(None, "已完成任务已清理")
