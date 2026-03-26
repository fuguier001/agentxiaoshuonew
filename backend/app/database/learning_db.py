# ==========================================
# 多 Agent 协作小说系统 - 学习系统数据库
# ==========================================

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json
import logging
import sqlite3

logger = logging.getLogger(__name__)


class LearningDatabase:
    """
    学习系统数据库 - 管理作品分析和学习数据
    """

    _instance: Optional['LearningDatabase'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._db_path = Path("./data/learning.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyzed_works (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT UNIQUE NOT NULL,
                author TEXT NOT NULL,
                title TEXT NOT NULL,
                text_length INTEGER DEFAULT 0,
                analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',
                analysis_json TEXT,
                style_features TEXT,
                narrative_style TEXT,
                description_style TEXT,
                dialogue_style TEXT,
                emotional_style TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS style_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT UNIQUE NOT NULL,
                author TEXT,
                work_title TEXT,
                feature_type TEXT,
                feature_name TEXT,
                description TEXT,
                examples TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS writing_techniques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                technique_id TEXT UNIQUE NOT NULL,
                author TEXT,
                work_title TEXT,
                technique_name TEXT,
                description TEXT,
                application TEXT,
                examples TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                project_id TEXT,
                chapter_num INTEGER,
                quality_score REAL,
                highlights TEXT,
                weaknesses TEXT,
                suggestions TEXT,
                analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyzed_works(analysis_id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("学习数据库初始化完成")

    def save_analyzed_work(self, analysis_id: str, author: str, title: str,
                          text_length: int, analysis_data: Dict[str, Any]) -> bool:
        """保存分析作品"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            style_features = json.dumps(analysis_data.get('style_features', []), ensure_ascii=False)
            narrative_style = json.dumps(analysis_data.get('narrative_style', []), ensure_ascii=False)
            description_style = json.dumps(analysis_data.get('description_style', []), ensure_ascii=False)
            dialogue_style = json.dumps(analysis_data.get('dialogue_style', []), ensure_ascii=False)
            emotional_style = json.dumps(analysis_data.get('emotional_style', []), ensure_ascii=False)

            cursor.execute('''
                INSERT OR REPLACE INTO analyzed_works
                (analysis_id, author, title, text_length, status, analysis_json,
                 style_features, narrative_style, description_style, dialogue_style, emotional_style)
                VALUES (?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                author,
                title,
                text_length,
                json.dumps(analysis_data, ensure_ascii=False),
                style_features,
                narrative_style,
                description_style,
                dialogue_style,
                emotional_style
            ))

            conn.commit()
            conn.close()

            for feature in analysis_data.get('style_features', []):
                self.save_style_feature(
                    feature_id=f"feat_{analysis_id}_{len(self.get_style_features())}",
                    author=author,
                    work_title=title,
                    feature_type=feature.get('type', 'unknown'),
                    feature_name=feature.get('name', ''),
                    description=feature.get('description', ''),
                    examples=json.dumps(feature.get('examples', []), ensure_ascii=False)
                )

            for technique in analysis_data.get('techniques', []):
                self.save_writing_technique(
                    technique_id=f"tech_{analysis_id}_{len(self.get_writing_techniques())}",
                    author=author,
                    work_title=title,
                    technique_name=technique.get('name', ''),
                    description=technique.get('description', ''),
                    application=technique.get('application', ''),
                    examples=json.dumps(technique.get('examples', []), ensure_ascii=False)
                )

            logger.info(f"保存分析作品：{author} - {title}")
            return True

        except Exception as e:
            logger.error(f"保存分析作品失败：{e}")
            return False

    def get_analyzed_work(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """获取分析作品"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM analyzed_works WHERE analysis_id = ?', (analysis_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_work_dict(row)
            return None

        except Exception as e:
            logger.error(f"获取分析作品失败：{e}")
            return None

    def get_all_analyzed_works(self) -> List[Dict[str, Any]]:
        """获取所有分析作品"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM analyzed_works ORDER BY analyzed_at DESC')
            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_work_dict(row) for row in rows]

        except Exception as e:
            logger.error(f"获取所有分析作品失败：{e}")
            return []

    def _row_to_work_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        try:
            style_features = json.loads(row['style_features']) if row['style_features'] else []
            narrative_style = json.loads(row['narrative_style']) if row['narrative_style'] else []
            description_style = json.loads(row['description_style']) if row['description_style'] else []
            dialogue_style = json.loads(row['dialogue_style']) if row['dialogue_style'] else []
            emotional_style = json.loads(row['emotional_style']) if row['emotional_style'] else []
        except:
            style_features = []
            narrative_style = []
            description_style = []
            dialogue_style = []
            emotional_style = []

        return {
            'analysis_id': row['analysis_id'],
            'author': row['author'],
            'title': row['title'],
            'text_length': row['text_length'],
            'analyzed_at': row['analyzed_at'],
            'status': row['status'],
            'style_features': style_features,
            'analysis': {
                'narrative_style': narrative_style,
                'description_style': description_style,
                'dialogue_style': dialogue_style,
                'emotional_style': emotional_style
            }
        }

    def delete_analyzed_work(self, analysis_id: str) -> bool:
        """删除分析作品"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM analyzed_works WHERE analysis_id = ?', (analysis_id,))
            conn.commit()
            conn.close()
            logger.info(f"删除分析作品：{analysis_id}")
            return True
        except Exception as e:
            logger.error(f"删除分析作品失败：{e}")
            return False

    def save_style_feature(self, feature_id: str, author: str, work_title: str,
                          feature_type: str, feature_name: str, description: str,
                          examples: str) -> bool:
        """保存风格特征"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO style_features
                (feature_id, author, work_title, feature_type, feature_name, description, examples)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (feature_id, author, work_title, feature_type, feature_name, description, examples))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"保存风格特征失败：{e}")
            return False

    def get_style_features(self, author: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取风格特征"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if author:
                cursor.execute('SELECT * FROM style_features WHERE author = ?', (author,))
            else:
                cursor.execute('SELECT * FROM style_features')
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"获取风格特征失败：{e}")
            return []

    def save_writing_technique(self, technique_id: str, author: str, work_title: str,
                               technique_name: str, description: str, application: str,
                               examples: str) -> bool:
        """保存写作技巧"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO writing_techniques
                (technique_id, author, work_title, technique_name, description, application, examples)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (technique_id, author, work_title, technique_name, description, application, examples))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"保存写作技巧失败：{e}")
            return False

    def get_writing_techniques(self, author: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取写作技巧"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if author:
                cursor.execute('SELECT * FROM writing_techniques WHERE author = ?', (author,))
            else:
                cursor.execute('SELECT * FROM writing_techniques')
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"获取写作技巧失败：{e}")
            return []

    def save_learning_analysis(self, analysis_id: str, project_id: str,
                               chapter_num: int, quality_score: float,
                               highlights: List[str], weaknesses: List[str],
                               suggestions: List[str]) -> bool:
        """保存学习分析"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO learning_analyses
                (analysis_id, project_id, chapter_num, quality_score, highlights, weaknesses, suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                project_id,
                chapter_num,
                quality_score,
                json.dumps(highlights, ensure_ascii=False),
                json.dumps(weaknesses, ensure_ascii=False),
                json.dumps(suggestions, ensure_ascii=False)
            ))

            conn.commit()
            conn.close()
            logger.info(f"保存学习分析：project={project_id}, chapter={chapter_num}")
            return True

        except Exception as e:
            logger.error(f"保存学习分析失败：{e}")
            return False

    def get_learning_analyses(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的学习分析"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM learning_analyses
                WHERE project_id = ?
                ORDER BY analyzed_at DESC
            ''', (project_id,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"获取学习分析失败：{e}")
            return []

    def get_learning_report(self, project_id: str) -> Dict[str, Any]:
        """获取学习报告"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM analyzed_works')
            analyzed_works_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM style_features')
            style_features_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM writing_techniques')
            techniques_count = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM learning_analyses WHERE project_id = ?',
                         (project_id,))
            chapters_evaluated = cursor.fetchone()['count']

            avg_score = 0.0
            if chapters_evaluated > 0:
                cursor.execute('SELECT AVG(quality_score) as avg FROM learning_analyses WHERE project_id = ?',
                            (project_id,))
                avg_score = cursor.fetchone()['avg'] or 0.0

            conn.close()

            recommendations = []
            if analyzed_works_count == 0:
                recommendations.append("配置 LLM API 后开始分析作品")
            if style_features_count < 5:
                recommendations.append("上传更多小说学习风格特征")
            if chapters_evaluated == 0:
                recommendations.append("开始创作章节，系统会自动评估质量")
            if avg_score < 7:
                recommendations.append("平均评分偏低，建议调整写作风格设置")

            return {
                'project_id': project_id,
                'analyzed_works': analyzed_works_count,
                'style_features_learned': style_features_count,
                'techniques_mastered': techniques_count,
                'chapters_evaluated': chapters_evaluated,
                'average_score': round(avg_score, 1),
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"获取学习报告失败：{e}")
            return {
                'project_id': project_id,
                'analyzed_works': 0,
                'style_features_learned': 0,
                'techniques_mastered': 0,
                'chapters_evaluated': 0,
                'average_score': 0.0,
                'recommendations': ["获取学习报告失败"]
            }


_learning_db: Optional[LearningDatabase] = None


def get_learning_database() -> LearningDatabase:
    """获取学习数据库单例"""
    global _learning_db
    if _learning_db is None:
        _learning_db = LearningDatabase()
    return _learning_db