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
            return await self.export_to_epub()
        
        else:
            raise ValueError(f"不支持的导出格式：{format}")

    async def export_to_epub(
        self,
        title: str = "未命名小说",
        author: str = "AI 创作",
        language: str = "zh-CN"
    ) -> str:
        """
        导出小说为 EPUB 格式

        Args:
            title: 小说标题
            author: 作者名称
            language: 语言代码

        Returns:
            导出文件路径
        """
        try:
            from ebooklib import epub
        except ImportError:
            logger.error("ebooklib 未安装，无法导出 EPUB")
            raise ImportError("请先安装 ebooklib: pip install ebooklib>=0.18")

        exports_dir = self.project_path / "exports"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = self._safe_filename(title)
        filepath = exports_dir / f"{safe_title}_{timestamp}.epub"

        # 创建 EPUB 书籍
        book = epub.EpubBook()

        # 设置元数据
        book.set_identifier(f"novel-{timestamp}")
        book.set_title(title)
        book.set_language(language)
        book.add_author(author)

        # 收集所有章节
        chapters_dir = self.project_path / "chapters"
        chapter_files = sorted(chapters_dir.glob("ch*.md"))

        if not chapter_files:
            raise ValueError("没有找到任何章节文件，无法导出")

        epub_chapters = []
        toc_links = []

        for idx, file in enumerate(chapter_files, start=1):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析章节信息
            chapter_info = self._parse_chapter_content(content, idx)

            # 创建 EPUB 章节
            chapter_filename = f"chapter_{idx:04d}.xhtml"
            epub_chapter = epub.EpubHtml(
                title=chapter_info['title'],
                file_name=chapter_filename,
                lang=language
            )

            # 设置章节内容
            epub_chapter.content = f"""
            <html>
            <head><title>{chapter_info['title']}</title></head>
            <body>
                <h1>{chapter_info['title']}</h1>
                {self._markdown_to_html(chapter_info['content'])}
            </body>
            </html>
            """

            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
            toc_links.append(epub_chapter)

        # 添加目录
        book.toc = tuple(toc_links)

        # 添加导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 设置样式
        style = '''
        body {
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            margin: 1em;
        }
        h1 {
            text-align: center;
            border-bottom: 1px solid #ccc;
            padding-bottom: 0.5em;
        }
        p {
            text-indent: 2em;
            margin: 0.5em 0;
        }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)

        # 设置 spine
        book.spine = ['nav'] + epub_chapters

        # 写入文件
        epub.write_epub(str(filepath), book, {})

        logger.info(f"EPUB 已导出：{filepath}")
        return str(filepath)

    def _parse_chapter_content(self, content: str, chapter_num: int) -> Dict[str, Any]:
        """解析章节内容，提取标题和正文"""
        lines = content.split('\n')
        title = f"第{chapter_num}章"
        body_lines = []
        in_frontmatter = False

        for line in lines:
            # 跳过 YAML frontmatter
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            # 提取标题
            if line.startswith('# ') and title == f"第{chapter_num}章":
                title = line[2:].strip()
                continue

            # 跳过元数据部分
            if line.startswith('---') or line.startswith('**'):
                continue

            body_lines.append(line)

        return {
            'title': title,
            'content': '\n'.join(body_lines).strip()
        }

    def _markdown_to_html(self, markdown_text: str) -> str:
        """简单的 Markdown 转 HTML"""
        html = markdown_text

        # 段落处理
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p:
                # 处理单行换行
                p = p.replace('\n', '<br/>')
                html_paragraphs.append(f'<p>{p}</p>')

        return '\n'.join(html_paragraphs)
    
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
