from typing import Any, Dict


class AutoService:
    async def create_novel(self, data: Dict[str, Any], resume: bool = True):
        from app.novel_architect import get_auto_creation_system
        from app.services.config_service import get_config_service

        title = data.get("title", "")
        if not title:
            raise ValueError("小说标题不能为空")

        # 获取 LLM 配置
        config_service = get_config_service()
        provider_config = config_service.get_active_provider_config()

        if not provider_config or not provider_config.get('api_key'):
            return {
                "status": "error",
                "error": "LLM 未配置，请先在设置中配置 LLM 提供商"
            }

        llm_client = {
            'api_key': provider_config['api_key'],
            'base_url': provider_config['base_url'],
            'endpoint': provider_config.get('endpoint', '/v1/chat/completions'),
            'model': provider_config['model'],
            'timeout': provider_config.get('timeout', 300)
        }

        system = get_auto_creation_system(llm_client)
        return await system.create_novel_from_scratch(
            title,
            data.get("genre", ""),
            data.get("description", ""),
            data.get("chapter_count", 3000),
            resume=resume
        )

    def get_blueprint(self, novel_id: str):
        from app.novel_db import get_novel_database

        db = get_novel_database()
        novel = db.get_novel(novel_id)
        if not novel:
            return None

        # 获取完整的蓝图设置
        settings = db.get_novel_settings(novel_id)

        return {
            "novel": novel,
            "stats": db.get_novel_stats(novel_id),
            "blueprint": {
                "world_map": settings.get("world_map", {}),
                "macro_plot": settings.get("macro_plot", {}),
                "character_system": settings.get("character_system", {}),
                "hook_network": settings.get("hook_network", {}),
                "chapter_count": settings.get("chapter_count", 0),
                "blueprint_created_at": settings.get("blueprint_created_at")
            }
        }


_auto_service: AutoService | None = None


def get_auto_service() -> AutoService:
    global _auto_service
    if _auto_service is None:
        _auto_service = AutoService()
    return _auto_service
