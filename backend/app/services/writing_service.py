from typing import Any, Dict

from app.novel_db import get_novel_database
from app.services.chapter_service import get_chapter_service
from app.workflow_executor import get_workflow_executor


class WritingService:
    def __init__(self):
        self.db = get_novel_database()
        self.chapter_service = get_chapter_service()

    async def create_chapter_workflow(self, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        chapter_num = chapter_data.get("chapter_num", 1)
        novel_id = chapter_data.get("novel_id", "default")
        outline = chapter_data.get("outline", "")
        word_count_target = chapter_data.get("word_count_target", 3000)
        style = chapter_data.get("style", "default")
        if not outline:
            raise ValueError("大纲不能为空")
        executor = get_workflow_executor()
        return await executor.execute_chapter_workflow(
            novel_id=novel_id,
            chapter_num=chapter_num,
            outline=outline,
            word_count_target=word_count_target,
            style=style,
        )

    def get_chapter(self, project_id: str, chapter_num: int):
        return self.chapter_service.get_chapter(project_id, chapter_num)

    def update_chapter(self, project_id: str, chapter_num: int, chapter_data: Dict[str, Any]):
        if not self.db.get_novel(project_id):
            return None
        return self.chapter_service.save_chapter(
            novel_id=project_id,
            chapter_num=chapter_num,
            content=chapter_data.get("content", ""),
            title=chapter_data.get("title", ""),
            outline=chapter_data.get("outline", ""),
            status=chapter_data.get("status", "draft"),
        )


_writing_service: WritingService | None = None


def get_writing_service() -> WritingService:
    global _writing_service
    if _writing_service is None:
        _writing_service = WritingService()
    return _writing_service
