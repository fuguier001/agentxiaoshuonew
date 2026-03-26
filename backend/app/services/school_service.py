from typing import Any, Dict, Optional


class SchoolService:
    def list_schools(self, category: Optional[str] = None):
        from app.database.school_db import get_school_database

        school_db = get_school_database()
        schools = school_db.get_all_schools(category)
        return {"schools": schools, "total": len(schools)}

    def get_school_detail(self, school_id: str):
        from app.database.school_db import get_school_database

        return get_school_database().get_school(school_id)

    def list_fused_styles(self):
        from app.database.school_db import get_school_database

        styles = get_school_database().get_all_fused_styles()
        return {"styles": styles, "total": len(styles)}

    def delete_fused_style(self, style_id: str) -> bool:
        from app.database.school_db import get_school_database

        return bool(get_school_database().delete_fused_style(style_id))

    def check_fusion_compatibility(self, school_ids: list[str]):
        from app.database.school_db import get_school_database

        if not school_ids:
            raise ValueError("请选择要检查的派系")
        return get_school_database().check_compatibility(school_ids)

    def fuse_schools(self, data: Dict[str, Any]):
        from app.database.school_db import get_school_database

        school_ids = data.get("school_ids", [])
        if len(school_ids) < 2:
            raise ValueError("至少需要选择2个派系进行融合")
        return get_school_database().fuse_schools(school_ids, data.get("fusion_name", "新风格"))

    def apply_style(self, style_id: str):
        from app.database.school_db import get_school_database

        if not style_id:
            raise ValueError("请指定要应用的风格ID")
        return get_school_database().get_fused_style(style_id)


_school_service: SchoolService | None = None


def get_school_service() -> SchoolService:
    global _school_service
    if _school_service is None:
        _school_service = SchoolService()
    return _school_service
