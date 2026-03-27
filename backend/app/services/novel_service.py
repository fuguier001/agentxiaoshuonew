from typing import Any, Dict, List
from datetime import datetime
import logging

from app.novel_db import get_novel_database
from app.services.chapter_service import get_chapter_service

logger = logging.getLogger(__name__)


class NovelService:
    def __init__(self):
        self.db = get_novel_database()
        self.chapter_service = get_chapter_service()

    def list_novels(self) -> List[Dict[str, Any]]:
        return self.db.get_all_novels()

    def create_novel(self, novel_data: Dict[str, Any]) -> Dict[str, Any]:
        title = novel_data.get("title", "")
        if not title:
            raise ValueError("小说标题不能为空")
        novel_id = self.db.create_novel(
            title=title,
            genre=novel_data.get("genre", "fantasy"),
            description=novel_data.get("description", ""),
            author=novel_data.get("author", "AI Author"),
        )
        return {"novel_id": novel_id, "title": title}

    def get_novel(self, novel_id: str) -> Dict[str, Any] | None:
        novel = self.db.get_novel(novel_id)
        if not novel:
            return None
        return {**novel, "stats": self.db.get_novel_stats(novel_id)}

    def update_novel(self, novel_id: str, novel_data: Dict[str, Any]) -> bool:
        if not self.db.get_novel(novel_id):
            return False
        self.db.update_novel(novel_id, **novel_data)
        return True

    def delete_novel(self, novel_id: str) -> None:
        self.db.delete_novel(novel_id)

    def list_characters(self, novel_id: str) -> List[Dict[str, Any]]:
        return self.db.get_characters(novel_id)

    def add_character(self, novel_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        name = character_data.get("name", "")
        if not name:
            raise ValueError("人物名称不能为空")
        character_id = self.db.add_character(
            novel_id,
            name=name,
            role=character_data.get("role", ""),
            description=character_data.get("description", ""),
            traits=character_data.get("traits", []),
        )
        return {"character_id": character_id, "name": name}

    def list_hooks(self, novel_id: str) -> List[Dict[str, Any]]:
        return self.db.get_unresolved_hooks(novel_id)

    def export_to_txt(self, novel_id: str) -> Dict[str, Any]:
        """导出小说为 TXT 格式

        Args:
            novel_id: 小说 ID

        Returns:
            包含文件名和内容的字典
        """
        # 获取小说信息
        novel = self.db.get_novel(novel_id)
        if not novel:
            raise ValueError("小说不存在")

        title = novel.get("title", "未命名小说")
        author = novel.get("author", "AI Author")
        description = novel.get("description", "")

        # 获取所有章节（按章节号排序）
        chapters = self.chapter_service.list_chapters(novel_id)
        chapters = sorted(chapters, key=lambda x: x.get("chapter_num", 0))

        if not chapters:
            raise ValueError("小说没有任何章节，无法导出")

        # 构建 TXT 内容
        lines = []

        # 标题和作者
        lines.append("=" * 50)
        lines.append(f"《{title}》")
        lines.append(f"作者：{author}")
        lines.append("=" * 50)
        lines.append("")

        # 简介
        if description:
            lines.append("【简介】")
            lines.append(description)
            lines.append("")
            lines.append("-" * 50)
            lines.append("")

        # 统计信息
        total_words = sum(len(ch.get("content") or "") for ch in chapters)
        lines.append(f"总章节数：{len(chapters)}")
        lines.append(f"总字数：约 {total_words} 字")
        lines.append(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("=" * 50)
        lines.append("")
        lines.append("")

        # 章节内容
        for chapter in chapters:
            chapter_num = chapter.get("chapter_num", 0)
            chapter_title = chapter.get("title") or f"第{chapter_num}章"
            content = chapter.get("content") or ""

            # 章节标题
            lines.append(f"第{chapter_num}章 {chapter_title}")
            lines.append("")

            # 章节正文
            if content:
                lines.append(content)
            else:
                lines.append("[此章节暂无内容]")

            lines.append("")
            lines.append("")
            lines.append("-" * 30)
            lines.append("")

        # 生成文件名
        safe_title = self._safe_filename(title)
        filename = f"{safe_title}.txt"

        # 合并内容
        txt_content = "\n".join(lines)

        logger.info(f"小说《{title}》导出成功，共 {len(chapters)} 章，约 {total_words} 字")

        return {
            "filename": filename,
            "content": txt_content,
            "total_chapters": len(chapters),
            "total_words": total_words,
            "title": title
        }

    def _safe_filename(self, title: str) -> str:
        """生成安全文件名"""
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in unsafe_chars:
            title = title.replace(char, '')
        return title[:50].strip()


_novel_service: NovelService | None = None


def get_novel_service() -> NovelService:
    global _novel_service
    if _novel_service is None:
        _novel_service = NovelService()
    return _novel_service
