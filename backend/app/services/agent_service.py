from datetime import datetime
from typing import Any, Dict, Optional


class AgentService:
    def get_agents_status(self) -> Dict[str, Any]:
        from app.agents.registry import get_agent_status

        agents = get_agent_status()
        return {
            "agents": list(agents.values()),
            "total": len(agents),
            "timestamp": datetime.now().isoformat(),
        }

    async def execute_agent_task(self, agent_id: str, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.agents.registry import get_agent

        agent = get_agent(agent_id)
        if not agent:
            return None
        return await agent.execute(task)

    def get_task_status(self, task_id: str):
        from app.tasks.task_manager import TaskStatus, get_task_manager

        manager = get_task_manager()
        task = manager.get_task(task_id)
        if not task:
            return None
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
            "progress": task.progress,
            "current_stage": task.current_stage,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "metadata": task.metadata,
        }

    def cancel_task(self, task_id: str) -> str | None:
        from app.tasks.task_manager import TaskStatus, get_task_manager

        manager = get_task_manager()
        task = manager.get_task(task_id)
        if not task:
            return None
        if task.status == TaskStatus.COMPLETED:
            raise ValueError("已完成的任务无法取消")
        manager.update_task(task_id, status=TaskStatus.CANCELLED)
        return task_id

    def list_tasks(self, status: Optional[str] = None, task_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        from app.tasks.task_manager import TaskStatus, get_task_manager

        manager = get_task_manager()
        tasks = manager.get_all_tasks()
        if status:
            tasks = [t for t in tasks if (t.status.value if isinstance(t.status, TaskStatus) else t.status) == status]
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        tasks = sorted(tasks, key=lambda x: x.created_at or datetime.min, reverse=True)[:limit]
        return {"tasks": [t.to_dict() for t in tasks], "total": len(tasks)}

    def clear_completed_tasks(self) -> None:
        from app.tasks.task_manager import get_task_manager

        manager = get_task_manager()
        manager.clear_completed_tasks()


_agent_service: AgentService | None = None


def get_agent_service() -> AgentService:
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
