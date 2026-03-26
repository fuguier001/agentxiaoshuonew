# ==========================================
# 多 Agent 协作小说系统 - 统一异常处理
# ==========================================

class NovelAgentException(Exception):
    """
    系统基类异常
    所有自定义异常都继承自此类
    """
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


# ========== LLM 相关异常 ==========

class LLMProviderError(NovelAgentException):
    """LLM 提供商错误"""
    def __init__(self, message: str, provider: str = None, status_code: int = None):
        # 直接调用 NovelAgentException 的__init__
        self.provider = provider
        self.status_code = status_code
        details = {"provider": provider, "status_code": status_code}
        super().__init__(
            message=message,
            code="LLM_PROVIDER_ERROR",
            details=details
        )


class LLMRateLimitError(LLMProviderError):
    """LLM 速率限制错误"""
    def __init__(self, provider: str, retry_after: int = None):
        super().__init__(
            message=f"API 速率限制，请稍后重试",
            provider=provider,
            status_code=429
        )
        self.retry_after = retry_after


class LLMTimeoutError(LLMProviderError):
    """LLM 调用超时"""
    def __init__(self, provider: str, timeout: int = None):
        super().__init__(
            message=f"LLM 调用超时",
            provider=provider,
            status_code=504
        )
        self.timeout = timeout


class LLMConfigError(LLMProviderError):
    """LLM 配置错误"""
    def __init__(self, message: str, missing_fields: list = None):
        # 调用 LLMProviderError 的__init__，使用位置参数
        super().__init__(message=message)
        # 覆盖 code
        self.code = "LLM_CONFIG_ERROR"
        self.missing_fields = missing_fields
        if missing_fields:
            self.details["missing_fields"] = missing_fields


# ========== 记忆系统异常 ==========

class MemoryError(NovelAgentException):
    """记忆系统错误"""
    def __init__(self, message: str, memory_type: str = None):
        super().__init__(
            message=message,
            code="MEMORY_ERROR",
            details={"memory_type": memory_type}
        )


class VectorStoreError(MemoryError):
    """向量数据库错误"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, memory_type="vector_store")
        if operation:
            self.details["operation"] = operation


class KnowledgeGraphError(MemoryError):
    """知识图谱错误"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, memory_type="knowledge_graph")
        if operation:
            self.details["operation"] = operation


class MemoryNotFoundError(MemoryError):
    """记忆未找到"""
    def __init__(self, memory_id: str = None, query: str = None):
        super().__init__(
            message="未找到相关记忆",
            memory_type="unknown"
        )
        if memory_id:
            self.details["memory_id"] = memory_id
        if query:
            self.details["query"] = query


# ========== Agent 相关异常 ==========

class AgentExecutionError(NovelAgentException):
    """Agent 执行错误"""
    def __init__(self, agent_id: str, message: str, task: dict = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            details={"agent_id": agent_id, "task": task}
        )


class AgentTimeoutError(AgentExecutionError):
    """Agent 执行超时"""
    def __init__(self, agent_id: str, timeout: int = None):
        super().__init__(
            agent_id=agent_id,
            message=f"Agent 执行超时",
            task=None
        )
        self.timeout = timeout


class AgentCircuitBreakerError(AgentExecutionError):
    """Agent 熔断器触发"""
    def __init__(self, agent_id: str, failure_count: int = None):
        super().__init__(
            agent_id=agent_id,
            message=f"Agent 熔断器触发，暂时停止服务",
            task=None
        )
        self.failure_count = failure_count
        if failure_count:
            self.details["failure_count"] = failure_count


class AgentNotRegisteredError(AgentExecutionError):
    """Agent 未注册"""
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            message=f"Agent 未注册：{agent_id}"
        )


# ========== 派系系统异常 ==========

class SchoolFusionError(NovelAgentException):
    """派系融合错误"""
    def __init__(self, message: str, school_ids: list = None, conflicts: list = None):
        super().__init__(
            message=message,
            code="SCHOOL_FUSION_ERROR",
            details={
                "school_ids": school_ids,
                "conflicts": conflicts or []
            }
        )


class SchoolIncompatibleError(SchoolFusionError):
    """派系不兼容"""
    def __init__(self, school1: str, school2: str, reason: str = None):
        super().__init__(
            message=f"派系不兼容：{school1} 与 {school2}",
            school_ids=[school1, school2],
            conflicts=[{"reason": reason}] if reason else []
        )


class SchoolNotFoundError(NovelAgentException):
    """派系未找到"""
    def __init__(self, school_id: str):
        super().__init__(
            message=f"派系未找到：{school_id}",
            code="SCHOOL_NOT_FOUND",
            details={"school_id": school_id}
        )


# ========== 文件存储异常 ==========

class StorageError(NovelAgentException):
    """文件存储错误"""
    def __init__(self, message: str, path: str = None, operation: str = None):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            details={"path": path, "operation": operation}
        )


class FileSaveError(StorageError):
    """文件保存错误"""
    def __init__(self, filename: str, reason: str = None):
        super().__init__(
            message=f"文件保存失败：{filename}",
            path=filename,
            operation="save"
        )
        if reason:
            self.details["reason"] = reason


class FileNotFound(StorageError):
    """文件未找到"""
    def __init__(self, filename: str):
        super().__init__(
            message=f"文件未找到：{filename}",
            path=filename,
            operation="read"
        )


# ========== 配置相关异常 ==========

class ConfigError(NovelAgentException):
    """配置错误"""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            details={"config_key": config_key}
        )


class ConfigValidationError(ConfigError):
    """配置验证失败"""
    def __init__(self, errors: list):
        super().__init__(
            message="配置验证失败",
            config_key="multiple"
        )
        self.errors = errors
        self.details["validation_errors"] = errors


class ConfigEncryptionError(ConfigError):
    """配置加密错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFIG_ENCRYPTION_ERROR"
        )


# ========== 任务队列异常 ==========

class TaskQueueError(NovelAgentException):
    """任务队列错误"""
    def __init__(self, message: str, task_id: str = None):
        super().__init__(
            message=message,
            code="TASK_QUEUE_ERROR",
            details={"task_id": task_id}
        )


class TaskTimeoutError(TaskQueueError):
    """任务超时"""
    def __init__(self, task_id: str, timeout: int = None):
        super().__init__(
            message=f"任务执行超时",
            task_id=task_id
        )
        self.timeout = timeout


class TaskNotFoundError(TaskQueueError):
    """任务未找到"""
    def __init__(self, task_id: str):
        super().__init__(
            message=f"任务未找到：{task_id}",
            task_id=task_id
        )


# ========== API 相关异常 ==========

class APIError(NovelAgentException):
    """API 错误"""
    def __init__(self, message: str, status_code: int = 500, endpoint: str = None):
        super().__init__(
            message=message,
            code="API_ERROR",
            details={"endpoint": endpoint}
        )
        self.status_code = status_code


class BadRequestError(APIError):
    """请求参数错误"""
    def __init__(self, message: str, invalid_params: list = None):
        super().__init__(
            message=message,
            status_code=400
        )
        if invalid_params:
            self.details["invalid_params"] = invalid_params


class UnauthorizedError(APIError):
    """未授权"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            message=message,
            status_code=401
        )


class ForbiddenError(APIError):
    """禁止访问"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403
        )


class NotFoundError(APIError):
    """资源未找到"""
    def __init__(self, resource: str = None, resource_id: str = None):
        message = "资源未找到"
        if resource:
            message = f"{resource}未找到"
        if resource_id:
            message = f"{resource}未找到：{resource_id}"
        
        super().__init__(
            message=message,
            status_code=404
        )


# ========== 全局异常处理器 ==========
# 在 backend/app/main.py 中注册

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


async def novel_agent_exception_handler(request: Request, exc: NovelAgentException):
    """NovelAgentException 统一处理"""
    logger.error(f"NovelAgentException: {exc.code} - {exc.message}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=exc.to_dict(),
        headers={"X-Error-Code": exc.code}
    )


async def api_error_handler(request: Request, exc: APIError):
    """APIError 统一处理"""
    logger.warning(f"APIError: {exc.status_code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求参数验证错误"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": {"errors": exc.errors()}
        }
    )


async def pydantic_exception_handler(request: Request, exc: ValidationError):
    """Pydantic 验证错误"""
    logger.warning(f"Pydantic validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "code": "VALIDATION_ERROR",
            "message": "数据验证失败",
            "details": {"errors": exc.errors()}
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """未捕获的通用异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "details": {}
        }
    )


# 注册异常处理器的辅助函数
def register_exception_handlers(app):
    """注册所有异常处理器到 FastAPI 应用"""
    app.add_exception_handler(NovelAgentException, novel_agent_exception_handler)
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
