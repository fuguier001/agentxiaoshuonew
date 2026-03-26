# ==========================================
# 多 Agent 协作小说系统 - 知识图谱与一致性检查
# ==========================================

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from pathlib import Path
import logging
import json
import sqlite3

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    知识图谱 - 管理小说世界中的实体和关系
    """

    _instance: Optional['KnowledgeGraph'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._db_path = Path("./data/knowledge_graph.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._entity_cache: Dict[str, Dict[str, Any]] = {}
        self._relation_cache: List[Dict[str, Any]] = []
        self._init_db()
        self._load_cache()
        logger.info("知识图谱初始化完成")

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT UNIQUE NOT NULL,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                properties TEXT,
                first_appearance_chapter INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relation_id TEXT UNIQUE NOT NULL,
                source_entity_id TEXT NOT NULL,
                target_entity_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                description TEXT,
                properties TEXT,
                chapter_introduced INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_entity_id) REFERENCES entities(entity_id),
                FOREIGN KEY (target_entity_id) REFERENCES entities(entity_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consistency_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                issue_type TEXT,
                entity_id TEXT,
                description TEXT,
                severity TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _load_cache(self):
        """加载缓存"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM entities')
            for row in cursor.fetchall():
                entity = self._row_to_entity_dict(row)
                self._entity_cache[entity['entity_id']] = entity

            cursor.execute('SELECT * FROM relations')
            self._relation_cache = [self._row_to_relation_dict(row) for row in cursor.fetchall()]

            conn.close()
            logger.info(f"加载了 {len(self._entity_cache)} 个实体和 {len(self._relation_cache)} 个关系")

        except Exception as e:
            logger.error(f"加载缓存失败：{e}")

    def _row_to_entity_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将行转换为实体字典"""
        try:
            properties = json.loads(row['properties']) if row['properties'] else {}
        except:
            properties = {}

        return {
            'entity_id': row['entity_id'],
            'entity_type': row['entity_type'],
            'name': row['name'],
            'description': row['description'],
            'properties': properties,
            'first_appearance_chapter': row['first_appearance_chapter']
        }

    def _row_to_relation_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将行转换为关系字典"""
        try:
            properties = json.loads(row['properties']) if row['properties'] else {}
        except:
            properties = {}

        return {
            'relation_id': row['relation_id'],
            'source_entity_id': row['source_entity_id'],
            'target_entity_id': row['target_entity_id'],
            'relation_type': row['relation_type'],
            'description': row['description'],
            'properties': properties,
            'chapter_introduced': row['chapter_introduced']
        }

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        description: str = "",
        properties: Optional[Dict[str, Any]] = None,
        chapter_introduced: int = 0
    ) -> bool:
        """添加实体"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO entities
                (entity_id, entity_type, name, description, properties, first_appearance_chapter)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entity_id,
                entity_type,
                name,
                description,
                json.dumps(properties or {}, ensure_ascii=False),
                chapter_introduced
            ))

            conn.commit()
            conn.close()

            self._entity_cache[entity_id] = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'name': name,
                'description': description,
                'properties': properties or {},
                'first_appearance_chapter': chapter_introduced
            }

            logger.info(f"添加实体：{name} ({entity_type})")
            return True

        except Exception as e:
            logger.error(f"添加实体失败：{e}")
            return False

    def add_relation(
        self,
        relation_id: str,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: str,
        description: str = "",
        properties: Optional[Dict[str, Any]] = None,
        chapter_introduced: int = 0
    ) -> bool:
        """添加关系"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO relations
                (relation_id, source_entity_id, target_entity_id, relation_type, description, properties, chapter_introduced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                relation_id,
                source_entity_id,
                target_entity_id,
                relation_type,
                description,
                json.dumps(properties or {}, ensure_ascii=False),
                chapter_introduced
            ))

            conn.commit()
            conn.close()

            self._relation_cache.append({
                'relation_id': relation_id,
                'source_entity_id': source_entity_id,
                'target_entity_id': target_entity_id,
                'relation_type': relation_type,
                'description': description,
                'properties': properties or {},
                'chapter_introduced': chapter_introduced
            })

            logger.info(f"添加关系：{relation_type}")
            return True

        except Exception as e:
            logger.error(f"添加关系失败：{e}")
            return False

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体"""
        return self._entity_cache.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """按类型获取实体"""
        return [e for e in self._entity_cache.values() if e['entity_type'] == entity_type]

    def get_relations(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体的所有关系"""
        return [
            r for r in self._relation_cache
            if r['source_entity_id'] == entity_id or r['target_entity_id'] == entity_id
        ]

    def get_entity_graph(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """获取实体图谱"""
        visited = set()
        graph = {'nodes': [], 'edges': []}

        def dfs(current_id: str, current_depth: int):
            if current_id in visited or current_depth > depth:
                return
            visited.add(current_id)

            entity = self.get_entity(current_id)
            if entity:
                graph['nodes'].append({
                    'id': entity['entity_id'],
                    'name': entity['name'],
                    'type': entity['entity_type']
                })

            for relation in self.get_relations(current_id):
                if relation['relation_id'] not in visited:
                    graph['edges'].append({
                        'source': relation['source_entity_id'],
                        'target': relation['target_entity_id'],
                        'type': relation['relation_type']
                    })
                    dfs(relation['target_entity_id'], current_depth + 1)

        dfs(entity_id, 0)
        return graph


class ConsistencyChecker:
    """
    一致性检查器 - 检查小说内容的一致性问题
    """

    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.issue_types = {
            'character_conflict': '人物冲突',
            'timeline_error': '时间线错误',
            'location_inconsistency': '地点不一致',
            'property_conflict': '属性冲突',
            'relation_conflict': '关系冲突'
        }

    async def check_content(self, content: str, chapter_num: int) -> List[Dict[str, Any]]:
        """检查内容一致性"""
        issues = []

        issues.extend(await self._check_character_consistency(content, chapter_num))
        issues.extend(await self._check_timeline_consistency(content, chapter_num))
        issues.extend(await self._check_location_consistency(content, chapter_num))

        return issues

    async def _check_character_consistency(
        self,
        content: str,
        chapter_num: int
    ) -> List[Dict[str, Any]]:
        """检查人物一致性"""
        issues = []

        character_entities = self.knowledge_graph.get_entities_by_type('character')

        for entity in character_entities:
            name = entity['name']
            if name in content:
                properties = entity.get('properties', {})

                if properties.get('gender') and properties['gender'] not in content[:500]:
                    pass

                if properties.get('age') and 'age' in content.lower():
                    age_mentioned = self._extract_age_mentions(content)
                    if age_mentioned and abs(age_mentioned - properties['age']) > 5:
                        issues.append({
                            'issue_type': 'character_conflict',
                            'severity': 'medium',
                            'entity_id': entity['entity_id'],
                            'description': f"角色 {name} 的年龄可能不一致：预期 {properties['age']} 岁，文中提到 {age_mentioned} 岁",
                            'chapter': chapter_num
                        })

        return issues

    async def _check_timeline_consistency(
        self,
        content: str,
        chapter_num: int
    ) -> List[Dict[str, Any]]:
        """检查时间线一致性"""
        issues = []

        time_keywords = ['昨天', '今天', '明天', '前天', '后天', '一周前', '一个月前', '一年前']
        for keyword in time_keywords:
            if keyword in content:
                issues.append({
                    'issue_type': 'timeline_warning',
                    'severity': 'low',
                    'description': f"注意时间描述：'{keyword}'",
                    'chapter': chapter_num
                })

        return issues

    async def _check_location_consistency(
        self,
        content: str,
        chapter_num: int
    ) -> List[Dict[str, Any]]:
        """检查地点一致性"""
        issues = []

        location_entities = self.knowledge_graph.get_entities_by_type('location')

        for entity in location_entities:
            name = entity['name']
            if name in content:
                first_appearance = entity.get('first_appearance_chapter', 0)
                if chapter_num > first_appearance + 10:
                    if '第一次来到' in content or '来到' in content and name in content:
                        issues.append({
                            'issue_type': 'location_inconsistency',
                            'severity': 'medium',
                            'entity_id': entity['entity_id'],
                            'description': f"角色似乎第一次来到 {name}，但该地点在第 {first_appearance} 章已出现",
                            'chapter': chapter_num
                        })

        return issues

    def _extract_age_mentions(self, content: str) -> Optional[int]:
        """提取文中提到的年龄"""
        import re
        patterns = [
            r'(\d+)岁',
            r'年龄(\d+)',
            r'年纪(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return None

    async def extract_entities_from_text(self, text: str, chapter_num: int) -> Dict[str, List[str]]:
        """从文本中提取实体"""
        entities = {
            'characters': [],
            'locations': [],
            'items': []
        }

        import re
        name_pattern = r'([A-Z][a-z]{1,10})'
        potential_names = re.findall(name_pattern, text)

        for name in potential_names:
            if len(name) >= 2 and name not in ['这是一个', '只见那', '忽然']:
                entities['characters'].append(name)

        location_keywords = ['来到', '去了', '进入', '走出', '到达']
        for keyword in location_keywords:
            if keyword in text:
                idx = text.find(keyword)
                potential_location = text[idx:idx+20]
                entities['locations'].append(potential_location.strip())

        return entities


_consistency_checker: Optional[ConsistencyChecker] = None


def get_consistency_checker() -> ConsistencyChecker:
    """获取一致性检查器单例"""
    global _consistency_checker
    if _consistency_checker is None:
        _consistency_checker = ConsistencyChecker()
    return _consistency_checker