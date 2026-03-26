# ==========================================
# 多 Agent 协作小说系统 - API 路由模块
# ==========================================

from fastapi import APIRouter
from . import agent_routes
from . import ai_routes
from . import auto_routes
from . import config_routes
from . import health
from . import learning_routes
from . import novel_routes
from . import school_routes
from . import writing_routes
from . import ws_routes

router = APIRouter()

router.include_router(novel_routes.router)
router.include_router(ai_routes.router)
router.include_router(auto_routes.router)
router.include_router(config_routes.router)
router.include_router(writing_routes.router)
router.include_router(learning_routes.router)
router.include_router(agent_routes.router)
router.include_router(school_routes.router)
router.include_router(health.router, prefix="/api")
router.include_router(ws_routes.router)

__all__ = ["agent_routes", "ai_routes", "auto_routes", "config_routes", "health", "learning_routes", "novel_routes", "school_routes", "writing_routes", "ws_routes"]
