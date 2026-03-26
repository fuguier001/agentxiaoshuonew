# ==========================================
# 多 Agent 协作小说系统 - 任务状态管理
# ==========================================

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """任务信息"""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        status: TaskStatus,
        progress: int = 0,
        current_stage: str = "",
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.status = status
        self.progress = progress
        self.current_stage = current_stage
        self.result = result
        self.error = error
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskInfo':
        status = data.get('status', 'pending')
        if isinstance(status, str):
            status = TaskStatus(status)
        return cls(
            task_id=data['task_id'],
            task_type=data.get('task_type', 'unknown'),
            status=status,
            progress=data.get('progress', 0),
            current_stage=data.get('current_stage', ''),
            result=data.get('result'),
            error=data.get('error'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            metadata=data.get('metadata', {})
        )


class TaskManager:
    """
    任务管理器 - 管理所有异步任务的状态
    """

    _instance: Optional['TaskManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._tasks: Dict[str, TaskInfo] = {}
        self._storage_path = Path("./data/tasks")
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._task_file = self._storage_path / "task_status.json"
        self._load_tasks()
        logger.info("任务管理器初始化完成")

    def _load_tasks(self):
        """从文件加载任务状态"""
        if self._task_file.exists():
            try:
                with open(self._task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = TaskInfo.from_dict(task_data)
                        self._tasks[task.task_id] = task
                logger.info(f"从文件加载了 {len(self._tasks)} 个任务")
            except Exception as e:
                logger.error(f"加载任务失败：{e}")

    def _save_tasks(self):
        """保存任务状态到文件"""
        try:
            data = {
                'tasks': [task.to_dict() for task in self._tasks.values()]
            }
            with open(self._task_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务失败：{e}")

    def create_task(
        self,
        task_id: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskInfo:
        """创建新任务"""
        task = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            progress=0,
            metadata=metadata or {}
        )
        self._tasks[task_id] = task
        self._save_tasks()
        logger.info(f"创建任务：{task_id} (类型：{task_type})")
        return task

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务"""
        return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        current_stage: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Optional[TaskInfo]:
        """更新任务状态"""
        task = self._tasks.get(task_id)
        if not task:
            logger.warning(f"任务不存在：{task_id}")
            return None

        if status is not None:
            task.status = status
        if progress is not None:
            task.progress = progress
        if current_stage is not None:
            task.current_stage = current_stage
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error

        task.updated_at = datetime.now()
        self._save_tasks()
        return task

    def get_all_tasks(self) -> List[TaskInfo]:
        """获取所有任务"""
        return list(self._tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> List[TaskInfo]:
        """获取指定状态的任务"""
        return [task for task in self._tasks.values() if task.status == status]

    def get_tasks_by_type(self, task_type: str) -> List[TaskInfo]:
        """获取指定类型的任务"""
        return [task for task in self._tasks.values() if task.task_type == task_type]

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save_tasks()
            logger.info(f"删除任务：{task_id}")
            return True
        return False

    def clear_completed_tasks(self):
        """清理已完成的任务"""
        completed = [tid for tid, task in self._tasks.items()
                     if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)]
        for tid in completed:
            del self._tasks[tid]
        if completed:
            self._save_tasks()
            logger.info(f"清理了 {len(completed)} 个已完成任务")


_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取任务管理器单例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def generate_task_id(prefix: str = "task") -> str:
    """生成唯一任务ID"""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"