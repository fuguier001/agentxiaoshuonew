from datetime import datetime
from typing import Any, Dict

from app.database import get_learning_database
from app.tasks.task_manager import TaskStatus, generate_task_id, get_task_manager
from app.workflow_executor import get_workflow_executor


def _extract_style_list(text: str) -> list:
    lines = text.strip().split('\n')
    styles = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) < 100:
            line = line.lstrip('0123456789.-、 ））')
            if line:
                styles.append(line)
    return styles[:5] if styles else [text[:50]]


def _extract_techniques(text: str) -> list:
    return [
        {"name": "场景转换", "description": "流畅的场景切换技巧", "application": "用于转场"},
        {"name": "人物刻画", "description": "通过言行展现人物性格", "application": "用于人物描写"},
        {"name": "悬念设置", "description": "在关键处设置悬念", "application": "用于吸引读者"},
    ]


class LearningService:
    async def analyze_work(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        learning_db = get_learning_database()
        task_manager = get_task_manager()
        author = analysis_data.get("author", "未知")
        title = analysis_data.get("title", "未知作品")
        text = analysis_data.get("text", "")
        if not text:
            raise ValueError("小说内容不能为空")

        task_id = generate_task_id("analysis")
        task_manager.create_task(task_id=task_id, task_type="work_analysis", metadata={"author": author, "title": title})
        task_manager.update_task(task_id, status=TaskStatus.RUNNING, progress=10, current_stage="开始分析作品")

        executor = get_workflow_executor()
        try:
            task_manager.update_task(task_id, progress=20, current_stage="分析叙事风格")
            narrative_result = await executor._call_llm(f"分析以下小说的叙事风格特点：\n{text[:5000]}\n\n请简洁回答，用中文。")
            task_manager.update_task(task_id, progress=40, current_stage="分析描写风格")
            description_result = await executor._call_llm(f"分析以下小说的描写风格特点：\n{text[:5000]}\n\n请简洁回答，用中文。")
            task_manager.update_task(task_id, progress=60, current_stage="分析对话风格")
            dialogue_result = await executor._call_llm(f"分析以下小说的对话风格特点：\n{text[:5000]}\n\n请简洁回答，用中文。")
            task_manager.update_task(task_id, progress=80, current_stage="分析情感风格")
            emotional_result = await executor._call_llm(f"分析以下小说的情感风格特点：\n{text[:5000]}\n\n请简洁回答，用中文。")
            task_manager.update_task(task_id, progress=90, current_stage="保存分析结果")

            analysis_result = {
                "status": "completed",
                "narrative_style": _extract_style_list(narrative_result),
                "description_style": _extract_style_list(description_result),
                "dialogue_style": _extract_style_list(dialogue_result),
                "emotional_style": _extract_style_list(emotional_result),
                "style_features": [
                    {"type": "narrative", "name": "叙事风格", "description": narrative_result},
                    {"type": "description", "name": "描写风格", "description": description_result},
                    {"type": "dialogue", "name": "对话风格", "description": dialogue_result},
                    {"type": "emotional", "name": "情感风格", "description": emotional_result},
                ],
                "techniques": _extract_techniques(text),
            }
            analysis_id = f"analysis_{author}_{title}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            learning_db.save_analyzed_work(
                analysis_id=analysis_id,
                author=author,
                title=title,
                text_length=len(text),
                analysis_data=analysis_result,
            )
            task_manager.update_task(task_id, status=TaskStatus.COMPLETED, progress=100, current_stage="分析完成", result={"analysis_id": analysis_id})
            return {"analysis_id": analysis_id, "author": author, "title": title, "analysis": analysis_result, "task_id": task_id}
        except Exception as e:
            task_manager.update_task(task_id, status=TaskStatus.FAILED, error=str(e))
            raise

    def get_analysis_status(self, analysis_id: str):
        work = get_learning_database().get_analyzed_work(analysis_id)
        if not work:
            return None
        return {"analysis_id": analysis_id, "status": work.get("status", "completed"), "progress": 100, "author": work.get("author"), "title": work.get("title"), "analyzed_at": work.get("analyzed_at")}

    def list_analyzed_works(self):
        works = get_learning_database().get_all_analyzed_works()
        return {"works": [{"analysis_id": w.get("analysis_id"), "author": w.get("author"), "title": w.get("title"), "analyzed_at": w.get("analyzed_at"), "chapter_count": len(w.get("analysis", {}).get("narrative_style", []))} for w in works], "total": len(works)}

    def delete_analyzed_work(self, analysis_id: str) -> bool:
        learning_db = get_learning_database()
        work = learning_db.get_analyzed_work(analysis_id)
        if not work:
            return False
        learning_db.delete_analyzed_work(analysis_id)
        return True

    def get_work_detail(self, analysis_id: str):
        return get_learning_database().get_analyzed_work(analysis_id)

    def get_learning_report(self, project_id: str = "default"):
        return get_learning_database().get_learning_report(project_id)


_learning_service: LearningService | None = None


def get_learning_service() -> LearningService:
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service
