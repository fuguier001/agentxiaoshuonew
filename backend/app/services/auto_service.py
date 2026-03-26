from typing import Any, Dict


class AutoService:
    async def create_novel(self, data: Dict[str, Any]):
        from app.novel_architect import get_auto_creation_system

        title = data.get("title", "")
        if not title:
            raise ValueError("小说标题不能为空")
        system = get_auto_creation_system()
        return await system.create_novel_from_scratch(
            title,
            data.get("genre", ""),
            data.get("description", ""),
            data.get("chapter_count", 3000),
        )

    def get_blueprint(self, novel_id: str):
        from app.novel_db import get_novel_database

        db = get_novel_database()
        novel = db.get_novel(novel_id)
        if not novel:
            return None
        return {"novel": novel, "stats": db.get_novel_stats(novel_id)}


_auto_service: AutoService | None = None


def get_auto_service() -> AutoService:
    global _auto_service
    if _auto_service is None:
        _auto_service = AutoService()
    return _auto_service
