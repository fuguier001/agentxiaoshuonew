from typing import Any, Dict


class AIService:
    def list_templates(self):
        from app.templates import list_templates as list_template_defs

        return list_template_defs()

    async def generate_outline(self, data: Dict[str, Any]):
        from app.workflow_executor import get_workflow_executor

        title = data.get("title", "")
        if not title:
            raise ValueError("小说标题不能为空")
        executor = get_workflow_executor()
        return await executor.generate_novel_outline(
            title,
            data.get("genre", ""),
            data.get("description", ""),
            data.get("template_id", "qichengzhuanhe"),
        )

    async def generate_characters(self, data: Dict[str, Any]):
        from app.workflow_executor import get_workflow_executor

        executor = get_workflow_executor()
        return await executor.generate_characters(
            data.get("title", ""),
            data.get("genre", ""),
            data.get("outline", ""),
            data.get("count", 5),
        )

    async def generate_chapter_outline(self, data: Dict[str, Any]):
        from app.workflow_executor import get_workflow_executor

        executor = get_workflow_executor()
        return await executor.generate_chapter_outline(
            data.get("novel_title", ""),
            data.get("chapter_num", 1),
            data.get("overall_outline", ""),
        )

    async def generate_plot(self, data: Dict[str, Any]):
        from app.workflow_executor import get_workflow_executor

        executor = get_workflow_executor()
        return await executor.generate_plot_design(data.get("outline", ""), data.get("characters", []))


_ai_service: AIService | None = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
