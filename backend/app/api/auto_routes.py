from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import logging

from app.api.responses import error_response, success_response
from app.services.auto_service import get_auto_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["全自动创作"])


@router.post("/auto/create")
async def auto_create_novel(data: Dict[str, Any]):
    try:
        title = data.get("title", "")
        result = await get_auto_service().create_novel(data)
        if result.get("status") == "success":
            return success_response({"novel_id": result["novel_id"], "blueprint": result["blueprint"], "first_chapter": result["first_chapter"]}, f"小说《{title}》创作完成！已生成世界观、3000 章规划和第一章")
        return error_response(result.get("error", "创作失败"), code="AUTO_CREATE_FAILED", details=result, status_code=400)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"全自动创作失败：{e}")
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
