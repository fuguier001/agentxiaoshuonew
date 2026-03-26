from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import logging

from app.services.writing_service import get_writing_service
from app.api.responses import error_response, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["写作流程"])


@router.post("/writing/chapter", name="create_writing_chapter")
async def create_writing_chapter(chapter_data: Dict[str, Any]):
    try:
        result = await get_writing_service().create_chapter_workflow(chapter_data)
        if result["status"] == "success":
            return success_response({
                "workflow_id": result["workflow_id"],
                "chapter_num": result["chapter_num"],
                "content": result["content"],
                "word_count": result["word_count"],
                "stages_completed": result["stages_completed"],
                "total_stages": result["total_stages"],
            }, "章节创作完成")
        return error_response(result.get("message", "创作失败"), code="WRITING_WORKFLOW_FAILED", details=result, status_code=400)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建章节失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/writing/chapter/{project_id}/{chapter_num}")
async def get_writing_chapter(project_id: str, chapter_num: int):
    try:
        chapter = get_writing_service().get_chapter(project_id, chapter_num)
        if chapter:
            return success_response(chapter)
        raise HTTPException(status_code=404, detail="章节未找到")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取章节失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/writing/chapter/{project_id}/{chapter_num}")
async def update_writing_chapter(project_id: str, chapter_num: int, chapter_data: Dict[str, Any]):
    try:
        chapter = get_writing_service().update_chapter(project_id, chapter_num, chapter_data)
        if not chapter:
            raise HTTPException(status_code=404, detail="小说不存在")
        return success_response({"chapter_num": chapter_num, "chapter": chapter})
    except Exception as e:
        logger.error(f"更新章节失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
