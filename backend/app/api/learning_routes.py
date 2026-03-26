from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import logging

from app.services.learning_service import get_learning_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["学习系统"])


@router.post("/learning/analyze")
async def analyze_work(analysis_data: Dict[str, Any]):
    try:
        result = await get_learning_service().analyze_work(analysis_data)
        return {"status": "success", "data": result, "message": "作品分析完成"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"分析作品失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    work = get_learning_service().get_analysis_status(analysis_id)
    if not work:
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "data": work}


@router.get("/learning/works")
async def list_analyzed_works():
    return {"status": "success", "data": get_learning_service().list_analyzed_works()}


@router.delete("/learning/works/{analysis_id}")
async def delete_analyzed_work(analysis_id: str):
    if not get_learning_service().delete_analyzed_work(analysis_id):
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "message": f"已删除分析：{analysis_id}"}


@router.get("/learning/works/{analysis_id}")
async def get_work_detail(analysis_id: str):
    work = get_learning_service().get_work_detail(analysis_id)
    if not work:
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "data": work}


@router.get("/learning/report")
async def get_learning_report(project_id: str = "default"):
    try:
        report = get_learning_service().get_learning_report(project_id)
        return {"status": "success", "data": report}
    except Exception as e:
        logger.error(f"获取学习报告失败：{e}")
        return {"status": "success", "data": {"project_id": project_id, "analyzed_works": 0, "style_features_learned": 0, "techniques_mastered": 0, "chapters_evaluated": 0, "average_score": 0.0, "recommendations": ["暂无数据"]}}
