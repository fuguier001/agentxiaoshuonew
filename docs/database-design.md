# 数据库设计文档

**版本**: v1.0  
**最后更新**: 2026-03-21

---

## 📋 目录

1. [数据库概览](#1-数据库概览)
2. [SQLite 表结构](#2-sqlite 表结构)
3. [向量数据库设计](#3-向量数据库设计)
4. [知识图谱设计](#4-知识图谱设计)
5. [文件存储结构](#5-文件存储结构)
6. [数据迁移](#6-数据迁移)

---

## 1. 数据库概览

### 1.1 数据库类型

| 用途 | 数据库 | 说明 |
|------|--------|------|
| 元数据存储 | SQLite | 项目/章节/人物/配置等结构化数据 |
| 语义检索 | Chroma | 文本向量化存储 |
| 关系网络 | NetworkX | 人物关系/情节关联等图谱数据 |
| 文件存储 | 本地文件系统 | 章节内容/配置文件等 |

### 1.2 数据库位置

```
novel-agent-system/
└── data/
    ├── novel.db              # SQLite 数据库
    ├── vector_db/            # Chroma 向量数据库
    ├── knowledge_graph/      # NetworkX 图谱数据
    └── backups/              # 备份文件
```

---

## 2. SQLite 表结构

### 2.1 项目表 (projects)

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    project_path TEXT NOT NULL,
    description TEXT,
    default_style_id TEXT,
    default_provider TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'deleted'))
);

CREATE INDEX idx_projects_status ON projects(status);
```

### 2.2 章节表 (chapters)

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    chapter_num INTEGER NOT NULL,
    title TEXT,
    outline TEXT,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'reviewing', 'published', 'archived')),
    version INTEGER DEFAULT 1,
    style_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    UNIQUE(project_id, chapter_num)
);

CREATE INDEX idx_chapters_project ON chapters(project_id);
CREATE INDEX idx_chapters_status ON chapters(status);
CREATE INDEX idx_chapters_num ON chapters(chapter_num);
```

### 2.3 章节版本表 (chapter_versions)

```sql
CREATE TABLE chapter_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT UNIQUE NOT NULL,
    chapter_id TEXT NOT NULL,
    version_num INTEGER NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER,
    revision_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    UNIQUE(chapter_id, version_num)
);

CREATE INDEX idx_chapter_versions_chapter ON chapter_versions(chapter_id);
```

### 2.4 人物表 (characters)

```sql
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT CHECK(role IN ('protagonist', 'antagonist', 'supporting', 'minor')),
    gender TEXT,
    age TEXT,
    description TEXT,
    background TEXT,
    personality TEXT,
    goals TEXT,
    relationships JSON,
    first_appearance_chapter INTEGER,
    last_appearance_chapter INTEGER,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'deceased')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_characters_project ON characters(project_id);
CREATE INDEX idx_characters_role ON characters(role);
```

### 2.5 人物关系表 (character_relationships)

```sql
CREATE TABLE character_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    character_id_1 TEXT NOT NULL,
    character_id_2 TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    description TEXT,
    strength INTEGER DEFAULT 5 CHECK(strength BETWEEN 1 AND 10),
    established_chapter INTEGER,
    changed_chapter INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id_1) REFERENCES characters(character_id),
    FOREIGN KEY (character_id_2) REFERENCES characters(character_id)
);

CREATE INDEX idx_relationships_project ON character_relationships(project_id);
CREATE INDEX idx_relationships_chars ON character_relationships(character_id_1, character_id_2);
```

### 2.6 情节线索表 (plot_threads)

```sql
CREATE TABLE plot_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    thread_name TEXT NOT NULL,
    thread_type TEXT CHECK(thread_type IN ('main', 'sub', 'romance', 'mystery', 'character_arc')),
    description TEXT,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'resolved', 'abandoned')),
    introduced_chapter INTEGER,
    resolved_chapter INTEGER,
    priority INTEGER DEFAULT 5 CHECK(priority BETWEEN 1 AND 10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_plot_threads_project ON plot_threads(project_id);
CREATE INDEX idx_plot_threads_status ON plot_threads(status);
```

### 2.7 伏笔表 (plot_hooks)

```sql
CREATE TABLE plot_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hook_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    thread_id TEXT,
    hook_type TEXT CHECK(hook_type IN ('foreshadowing', 'mystery', 'question', 'promise', 'threat')),
    description TEXT NOT NULL,
    chapter_introduced INTEGER NOT NULL,
    chapter_resolved INTEGER,
    status TEXT DEFAULT 'unresolved' CHECK(status IN ('unresolved', 'resolved', 'expired')),
    importance INTEGER DEFAULT 5 CHECK(importance BETWEEN 1 AND 10),
    related_characters JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (thread_id) REFERENCES plot_threads(thread_id)
);

CREATE INDEX idx_plot_hooks_project ON plot_hooks(project_id);
CREATE INDEX idx_plot_hooks_status ON plot_hooks(status);
```

### 2.8 风格库表 (style_library)

```sql
CREATE TABLE style_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    style_id TEXT UNIQUE NOT NULL,
    style_name TEXT NOT NULL,
    style_type TEXT CHECK(style_type IN ('learned', 'fused', 'custom')),
    source_work_id TEXT,
    source_school_ids JSON,
    description TEXT,
    style_dimensions JSON,
    writing_guidelines JSON,
    tone_examples JSON,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_work_id) REFERENCES analyzed_works(work_id)
);

CREATE INDEX idx_style_library_type ON style_library(style_type);
CREATE INDEX idx_style_library_active ON style_library(is_active);
```

### 2.9 已分析作品表 (analyzed_works)

```sql
CREATE TABLE analyzed_works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT UNIQUE NOT NULL,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    source_text_hash TEXT,
    chapter_count INTEGER,
    analysis_result JSON,
    extracted_patterns JSON,
    extracted_techniques JSON,
    assigned_school TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    analysis_duration_seconds INTEGER
);

CREATE INDEX idx_analyzed_works_author ON analyzed_works(author);
CREATE INDEX idx_analyzed_works_school ON analyzed_works(assigned_school);
```

### 2.10 学习报告表 (learning_reports)

```sql
CREATE TABLE learning_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    chapter_num INTEGER,
    score REAL,
    evaluation JSON,
    strengths JSON,
    weaknesses JSON,
    suggestions JSON,
    style_adjustments JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_learning_reports_project ON learning_reports(project_id);
CREATE INDEX idx_learning_reports_chapter ON learning_reports(chapter_num);
```

### 2.11 派系表 (schools)

```sql
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id TEXT UNIQUE NOT NULL,
    school_name TEXT NOT NULL,
    category TEXT NOT NULL,
    parent_school TEXT,
    description TEXT,
    key_features JSON,
    style_dimensions JSON,
    representative_works JSON,
    compatible_schools JSON,
    incompatible_schools JSON,
    member_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_schools_category ON schools(category);
```

### 2.12 任务队列表 (tasks)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    task_type TEXT NOT NULL,
    agent_id TEXT,
    project_id TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    input_data JSON,
    result_data JSON,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(task_type);
CREATE INDEX idx_tasks_created ON tasks(created_at);
```

### 2.13 系统日志表 (system_logs)

```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id TEXT UNIQUE NOT NULL,
    level TEXT CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module TEXT,
    message TEXT NOT NULL,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_created ON system_logs(created_at);
CREATE INDEX idx_logs_module ON system_logs(module);
```

---

## 3. 向量数据库设计

### 3.1 Chroma 集合结构

```python
# Chroma 集合定义
COLLECTIONS = {
    "chapters": "章节内容向量",
    "patterns": "写作模式向量",
    "techniques": "写作技巧向量",
    "styles": "风格特征向量"
}
```

### 3.2 chapters 集合

```python
{
    "id": "chapter_vec_001",
    "embedding": [0.1, 0.2, ...],  # 1536 维向量
    "metadata": {
        "chapter_id": "ch_001",
        "project_id": "proj_001",
        "chapter_num": 1,
        "word_count": 3000,
        "created_at": "2026-03-21T18:00:00",
        "style_id": "style_001"
    },
    "document": "章节全文或摘要"
}
```

### 3.3 patterns 集合

```python
{
    "id": "pattern_vec_001",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
        "pattern_id": "pat_001",
        "pattern_type": "narrative/dialogue/description/emotion",
        "pattern_name": "多线叙事",
        "source_work_id": "work_001",
        "school_id": "wuxia_jinyong"
    },
    "document": "模式描述 + 示例"
}
```

### 3.4 techniques 集合

```python
{
    "id": "tech_vec_001",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
        "technique_id": "tech_001",
        "category": "structure/dialogue/description/emotion/pace",
        "difficulty": "beginner/intermediate/advanced",
        "applicable_scenes": ["opening", "climax"]
    },
    "document": "技巧描述 + 步骤 + 示例"
}
```

### 3.5 检索策略

```python
# 多路召回检索
async def retrieve(query: str, collections: List[str], limit: int = 10):
    results = []
    
    # 为每个集合执行检索
    for collection_name in collections:
        collection = chroma_client.get_collection(collection_name)
        query_embedding = embed(query)
        
        query_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"]
        )
        
        results.extend(query_results)
    
    # 去重 + 重排序
    return rerank(results)
```

---

## 4. 知识图谱设计

### 4.1 节点类型

```python
NODE_TYPES = {
    "Character": "人物节点",
    "Chapter": "章节节点",
    "PlotThread": "情节线索节点",
    "PlotHook": "伏笔节点",
    "Location": "地点节点",
    "Event": "事件节点",
    "Style": "风格节点"
}
```

### 4.2 关系类型

```python
RELATIONSHIP_TYPES = {
    # 人物关系
    "FRIEND_OF": "朋友",
    "ENEMY_OF": "敌人",
    "LOVER_OF": "恋人",
    "FAMILY_OF": "家人",
    "MASTER_OF": "师徒",
    
    # 情节关系
    "APPEARS_IN": "出现在章节",
    "STARTS_THREAD": "开启线索",
    "RESOLVES_THREAD": "解决线索",
    "SETS_UP_HOOK": "埋设伏笔",
    "RESOLVES_HOOK": "回收伏笔",
    
    # 地点关系
    "LOCATED_IN": "位于",
    "VISITED_IN": "在章节中访问",
    
    # 风格关系
    "INFLUENCED_BY": "受风格影响",
    "USES_TECHNIQUE": "使用技巧"
}
```

### 4.3 图谱构建示例

```python
import networkx as nx

# 创建有向图
G = nx.DiGraph()

# 添加人物节点
G.add_node("char_001", type="Character", name="主角", role="protagonist")
G.add_node("char_002", type="Character", name="反派", role="antagonist")

# 添加人物关系
G.add_edge("char_001", "char_002", relationship="ENEMY_OF", strength=9, established_chapter=1)

# 添加章节节点
G.add_node("ch_001", type="Chapter", chapter_num=1, title="初遇")

# 添加人物与章节的关系
G.add_edge("char_001", "ch_001", relationship="APPEARS_IN")
G.add_edge("char_002", "ch_001", relationship="APPEARS_IN")

# 添加伏笔节点
G.add_node("hook_001", type="PlotHook", description="神秘身世", importance=8)

# 添加伏笔关系
G.add_edge("ch_001", "hook_001", relationship="SETS_UP_HOOK")
G.add_edge("char_001", "hook_001", relationship="RELATED_TO")
```

### 4.4 图谱查询示例

```python
# 查询人物的所有关系
def get_character_relationships(character_id: str):
    edges = G.edges(character_id, data=True)
    return [
        {
            "from": edge[0],
            "to": edge[1],
            "relationship": edge[2]["relationship"],
            "strength": edge[2].get("strength")
        }
        for edge in edges
    ]

# 查询未回收的伏笔
def get_unresolved_hooks():
    hooks = [node for node, data in G.nodes(data=True) if data.get("type") == "PlotHook"]
    unresolved = []
    
    for hook in hooks:
        # 检查是否有 RESOLVES_HOOK 关系
        resolved = any(
            data.get("relationship") == "RESOLVES_HOOK"
            for _, _, data in G.in_edges(hook, data=True)
        )
        if not resolved:
            unresolved.append(hook)
    
    return unresolved

# 查询人物的成长弧线
def get_character_arc(character_id: str):
    # 获取人物出现的所有章节
    chapters = [
        target
        for source, target, data in G.out_edges(character_id, data=True)
        if data.get("relationship") == "APPEARS_IN"
    ]
    
    # 按章节号排序
    chapters.sort(key=lambda ch: G.nodes[ch]["chapter_num"])
    
    return chapters
```

---

## 5. 文件存储结构

### 5.1 项目文件结构

```
projects/
└── [project_name]/
    ├── config.json              # 项目配置
    ├── outline/
    │   ├── main_outline.md      # 主线大纲
    │   └── sub_outlines/        # 支线大纲
    │       ├── thread_001.md
    │       └── thread_002.md
    ├── characters/
    │   ├── [character_name].md  # 人物设定
    │   └── relationships.json   # 人物关系网
    ├── chapters/
    │   ├── ch001_章节名.md
    │   ├── ch002_章节名.md
    │   └── ...
    ├── drafts/
    │   ├── ch005_draft_v1.md
    │   ├── ch005_draft_v2.md
    │   └── ...
    ├── memory/
    │   ├── vector_db/           # 项目专属向量库
    │   ├── knowledge_graph.json # 知识图谱快照
    │   └── timeline.json        # 时间线索引
    └── exports/
        ├── novel_complete.txt   # 合并全文
        └── novel.epub
```

### 5.2 章节文件格式

```markdown
---
chapter_num: 5
title: 初遇反派
word_count: 3245
status: published
created_at: 2026-03-21T18:00:00
style_id: fused_style_001
---

# 第 5 章 初遇反派

[章节正文...]

---
## 元数据

**出场人物**: 主角，反派，配角 A
**地点**: 京城街道
**时间**: 三月初三
**伏笔**: 
- 埋设：神秘身世 (hook_001)
- 回收：无

**写作技巧应用**:
- 多线交织 (tech_001)
- 反差塑造 (tech_005)
```

### 5.3 配置文件格式

```json
{
  "project_name": "我的小说",
  "project_id": "proj_001",
  "created_at": "2026-03-21T18:00:00",
  "default_style_id": "fused_style_001",
  "default_provider": "volcengine",
  "settings": {
    "auto_commit": true,
    "backup_enabled": true,
    "backup_interval_hours": 24
  },
  "statistics": {
    "total_chapters": 10,
    "total_words": 32450,
    "last_updated": "2026-03-21T18:00:00"
  }
}
```

---

## 6. 数据迁移

### 6.1 迁移脚本结构

```
migrations/
├── 001_initial_schema.sql
├── 002_add_character_relationships.sql
├── 003_add_plot_hooks.sql
└── ...
```

### 6.2 迁移示例

```sql
-- migrations/001_initial_schema.sql
-- 创建初始表结构

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 记录迁移版本
INSERT INTO schema_migrations (version, applied_at)
VALUES ('001', CURRENT_TIMESTAMP);
```

### 6.3 迁移管理

```python
class MigrationManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_current_version(self) -> str:
        """获取当前数据库版本"""
        # 查询 schema_migrations 表
        pass
    
    def get_pending_migrations(self) -> List[str]:
        """获取待执行的迁移"""
        current = self.get_current_version()
        all_migrations = self._list_migrations()
        return [m for m in all_migrations if m > current]
    
    def migrate(self, target_version: str = None):
        """执行迁移"""
        pending = self.get_pending_migrations()
        
        for migration in pending:
            logger.info(f"执行迁移：{migration}")
            sql = self._load_migration(migration)
            self._execute_sql(sql)
            self._record_migration(migration)
        
        logger.info("迁移完成")
```

---

**文档结束**
