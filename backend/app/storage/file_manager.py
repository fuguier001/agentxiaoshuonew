# ==========================================
# 多 Agent 协作小说系统 - 文件存储管理
# ==========================================

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import json
import shutil

logger = logging.getLogger(__name__)


class FileManager:
    """
    文件管理器
    
    负责:
    1. 章节文件保存
    2. 项目文件管理
    3. 版本控制（Git 集成）
    4. 导出功能
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self._ensure_directories()
        
        logger.info(f"文件管理器初始化：{project_path}")
    
    def _ensure_directories(self):
        """确保目录存在"""
        dirs = [
            self.project_path / "outline",
            self.project_path / "characters",
            self.project_path / "chapters",
            self.project_path / "drafts",
            self.project_path / "memory",
            self.project_path / "exports"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def save_chapter(
        self,
        chapter_num: int,
        content: str,
        title: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """保存章节"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        title = title or f"第{chapter_num}章"
        
        # 文件名
        safe_title = self._safe_filename(title)
        filename = f"ch{chapter_num:03d}_{safe_title}.md"
        filepath = self.project_path / "chapters" / filename
        
        # 构建 Markdown 内容
        markdown_content = self._build_markdown(chapter_num, title, content, metadata)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"章节已保存：{filepath}")
        
        # 保存到草稿（带时间戳）
        draft_filename = f"ch{chapter_num:03d}_draft_{timestamp}.md"
        draft_filepath = self.project_path / "drafts" / draft_filename
        
        with open(draft_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def _build_markdown(
        self,
        chapter_num: int,
        title: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """构建 Markdown 格式"""
        metadata = metadata or {}
        
        md = f"""---
chapter_num: {chapter_num}
title: {title}
word_count: {len(content)}
created_at: {datetime.now().isoformat()}
style_id: {metadata.get('style_id', 'default')}
---

# {title}

{content}

---
## 元数据

**字数**: {len(content)}
**创作时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**风格**: {metadata.get('style_name', '默认')}
**应用技巧**: {', '.join(metadata.get('techniques', []))}
"""
        return md
    
    def _safe_filename(self, title: str) -> str:
        """生成安全文件名"""
        # 移除非法字符
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in unsafe_chars:
            title = title.replace(char, '')
        
        # 限制长度
        return title[:50].strip()
    
    async def load_chapter(self, chapter_num: int) -> Optional[Dict[str, Any]]:
        """加载章节"""
        chapters_dir = self.project_path / "chapters"
        
        # 查找章节文件
        for file in chapters_dir.glob(f"ch{chapter_num:03d}_*.md"):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 Markdown
            return self._parse_markdown(content, file.name)
        
        return None
    
    def _parse_markdown(self, content: str, filename: str) -> Dict[str, Any]:
        """解析 Markdown"""
        # 简化解析
        return {
            "filename": filename,
            "content": content,
            "metadata": {}
        }
    
    async def export_novel(self, format: str = 'txt') -> str:
        """导出小说"""
        exports_dir = self.project_path / "exports"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'txt':
            filepath = exports_dir / f"novel_{timestamp}.txt"
            
            # 合并所有章节
            chapters = []
            for file in sorted((self.project_path / "chapters").glob("ch*.md")):
                with open(file, 'r', encoding='utf-8') as f:
                    chapters.append(f.read())
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n\n".join(chapters))
            
            logger.info(f"小说已导出：{filepath}")
            return str(filepath)
        
        elif format == 'epub':
            # TODO: EPUB 导出
            raise NotImplementedError("EPUB 导出暂未实现")
        
        else:
            raise ValueError(f"不支持的导出格式：{format}")
    
    def get_project_stats(self) -> Dict[str, Any]:
        """获取项目统计"""
        chapters_dir = self.project_path / "chapters"
        
        chapter_files = list(chapters_dir.glob("ch*.md"))
        total_words = 0
        
        for file in chapter_files:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单字数统计
                total_words += len(content)
        
        return {
            "total_chapters": len(chapter_files),
            "total_words": total_words,
            "project_path": str(self.project_path),
            "last_updated": datetime.now().isoformat()
        }


# ========== Git 版本控制 ==========

class GitVersionControl:
    """Git 版本控制"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git = None
        self._init_git()
    
    def _init_git(self):
        """初始化 Git"""
        try:
            import git
            
            if (self.project_path / ".git").exists():
                self.git = git.Repo(self.project_path)
            else:
                self.git = git.Repo.init(self.project_path)
                logger.info(f"Git 仓库初始化：{self.project_path}")
        except ImportError:
            logger.warning("GitPython 未安装，版本控制不可用")
        except Exception as e:
            logger.error(f"Git 初始化失败：{e}")
    
    def commit(self, message: str, files: List[str] = None):
        """提交更改"""
        if not self.git:
            return
        
        try:
            if files:
                for file in files:
                    self.git.index.add([file])
            else:
                self.git.index.add(["*"])
            
            self.git.index.commit(message)
            logger.info(f"Git 提交：{message}")
        except Exception as e:
            logger.error(f"Git 提交失败：{e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取提交历史"""
        if not self.git:
            return []
        
        history = []
        for commit in self.git.iter_commits(max_count=limit):
            history.append({
                "hash": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": datetime.fromtimestamp(commit.committed_date).isoformat()
            })
        
        return history


# ========== 全局工厂函数 ==========

def get_file_manager(project_path: str) -> FileManager:
    """获取文件管理器"""
    return FileManager(project_path)


def get_version_control(project_path: str) -> Optional[GitVersionControl]:
    """获取版本控制"""
    return GitVersionControl(project_path)
