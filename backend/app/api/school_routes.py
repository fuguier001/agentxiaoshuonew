from fastapi import APIRouter, HTTPException
from typing import Any, Dict, Optional

from app.api.responses import error_response, success_response
from app.services.school_service import get_school_service

router = APIRouter(prefix="/api", tags=["派系管理"])


@router.get("/schools")
async def list_schools(category: Optional[str] = None):
    return success_response(get_school_service().list_schools(category))


@router.get("/schools/{school_id}")
async def get_school_detail(school_id: str):
    school = get_school_service().get_school_detail(school_id)
    if not school:
        raise HTTPException(status_code=404, detail=f"派系不存在：{school_id}")
    return success_response(school)


@router.get("/schools/fused/all")
async def list_fused_styles():
    return success_response(get_school_service().list_fused_styles())


@router.delete("/schools/fused/{style_id}")
async def delete_fused_style(style_id: str):
    if not get_school_service().delete_fused_style(style_id):
        raise HTTPException(status_code=404, detail=f"融合风格不存在：{style_id}")
    return success_response(None, f"已删除融合风格：{style_id}")


@router.post("/schools/check-fusion")
async def check_fusion_compatibility(data: Dict[str, Any]):
    try:
        result = get_school_service().check_fusion_compatibility(data.get("school_ids", []))
        return success_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/schools/fuse")
async def fuse_schools(data: Dict[str, Any]):
    try:
        result = get_school_service().fuse_schools(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result.get("success"):
        return error_response(result.get("error", "融合失败"), code="SCHOOL_FUSION_FAILED", details=result.get("details"), status_code=400)
    return success_response(result)


@router.post("/schools/apply-style")
async def apply_style(data: Dict[str, Any]):
    try:
        style = get_school_service().apply_style(data.get("style_id"))
        style_id = data.get("style_id")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not style:
        raise HTTPException(status_code=404, detail=f"风格不存在：{style_id}")
    return success_response({"style_id": style_id, "style_name": style.get('style_name'), "style_features": style.get('style_features', [])}, f"风格 '{style.get('style_name')}' 已应用到当前项目")
