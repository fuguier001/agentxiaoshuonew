# ==========================================
# 配置数据库管理工具
# 使用 SQLite 持久化存储 LLM 配置
# ==========================================

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ConfigDatabase:
    """
    配置数据库管理类
    使用 SQLite 存储 LLM 配置、项目设置等
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认使用 backend/data/config.db
            db_path = Path(__file__).parent.parent / 'data' / 'config.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建 LLM 配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                api_format TEXT DEFAULT 'openai',
                api_key TEXT,
                base_url TEXT NOT NULL,
                endpoint TEXT DEFAULT '/v1/chat/completions',
                model TEXT,
                auth_type TEXT DEFAULT 'bearer',
                auth_header TEXT,
                headers TEXT DEFAULT '{}',
                timeout INTEGER DEFAULT 60,
                use_stream INTEGER DEFAULT 1,
                response_format TEXT DEFAULT 'openai',
                response_path TEXT,
                enabled INTEGER DEFAULT 1,
                rate_limit INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建项目配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_path TEXT NOT NULL,
                default_provider TEXT,
                auto_commit INTEGER DEFAULT 1,
                git_author_name TEXT DEFAULT 'Novel Agent',
                git_author_email TEXT DEFAULT 'novel-agent@local',
                backup_interval INTEGER DEFAULT 24,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认系统配置
        cursor.execute('''
            INSERT OR IGNORE INTO system_config (key, value, description)
            VALUES ('default_provider', 'eggfans', '默认 LLM 提供商')
        ''')
        
        # 插入默认项目配置
        cursor.execute('''
            INSERT OR IGNORE INTO project_config 
            (id, project_name, project_path, default_provider)
            VALUES (1, '我的小说', './projects/我的小说', 'eggfans')
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"数据库初始化完成：{self.db_path}")
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _deserialize_provider_row(self, row) -> Dict[str, Any]:
        """将数据库行转换为 provider 配置字典"""
        data = dict(row)

        headers = data.get('headers')
        if isinstance(headers, str):
            try:
                data['headers'] = json.loads(headers) if headers else {}
            except json.JSONDecodeError:
                logger.warning(f"解析 provider headers 失败，已回退为空对象：{data.get('name')}")
                data['headers'] = {}
        elif headers is None:
            data['headers'] = {}

        data['enabled'] = bool(data.get('enabled', 1))
        data['use_stream'] = bool(data.get('use_stream', 1))
        return data

    def _save_provider_with_cursor(self, cursor, name: str, config: Dict[str, Any]):
        cursor.execute('SELECT id FROM llm_providers WHERE name = ?', (name,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute(
                '''
                    UPDATE llm_providers SET
                        api_format = ?,
                        api_key = ?,
                        base_url = ?,
                        endpoint = ?,
                        model = ?,
                        auth_type = ?,
                        auth_header = ?,
                        headers = ?,
                        timeout = ?,
                        use_stream = ?,
                        response_format = ?,
                        response_path = ?,
                        enabled = ?,
                        rate_limit = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                ''',
                (
                    config.get('api_format', 'openai'),
                    config.get('api_key', ''),
                    config.get('base_url', ''),
                    config.get('endpoint', '/v1/chat/completions'),
                    config.get('model', ''),
                    config.get('auth_type', 'bearer'),
                    config.get('auth_header'),
                    json.dumps(config.get('headers', {})),
                    config.get('timeout', 60),
                    1 if config.get('use_stream', True) else 0,
                    config.get('response_format', 'openai'),
                    config.get('response_path'),
                    1 if config.get('enabled', True) else 0,
                    config.get('rate_limit'),
                    name,
                ),
            )
        else:
            cursor.execute(
                '''
                    INSERT INTO llm_providers
                    (name, api_format, api_key, base_url, endpoint, model,
                     auth_type, auth_header, headers, timeout, use_stream, response_format,
                     response_path, enabled, rate_limit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    name,
                    config.get('api_format', 'openai'),
                    config.get('api_key', ''),
                    config.get('base_url', ''),
                    config.get('endpoint', '/v1/chat/completions'),
                    config.get('model', ''),
                    config.get('auth_type', 'bearer'),
                    config.get('auth_header'),
                    json.dumps(config.get('headers', {})),
                    config.get('timeout', 60),
                    1 if config.get('use_stream', True) else 0,
                    config.get('response_format', 'openai'),
                    config.get('response_path'),
                    1 if config.get('enabled', True) else 0,
                    config.get('rate_limit'),
                ),
            )

    def save_provider_with_connection(self, conn, name: str, config: Dict[str, Any]) -> bool:
        self._save_provider_with_cursor(conn.cursor(), name, config)
        return True

    def set_system_config_with_connection(self, conn, key: str, value: str, description: str = None) -> bool:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM system_config WHERE key = ?', (key,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute(
                '''
                    UPDATE system_config SET
                        value = ?,
                        description = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                ''',
                (value, description, key),
            )
        else:
            cursor.execute(
                '''
                    INSERT INTO system_config (key, value, description)
                    VALUES (?, ?, ?)
                ''',
                (key, value, description),
            )
        return True
    
    # ========== LLM 提供商管理 ==========
    
    def save_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """保存 LLM 提供商配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            self._save_provider_with_cursor(cursor, name, config)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"保存 LLM 提供商配置失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """获取 LLM 提供商配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM llm_providers WHERE name = ?', (name,))
            row = cursor.fetchone()
            
            if row:
                return self._deserialize_provider_row(row)
            return None
        except Exception as e:
            logger.error(f"获取 LLM 提供商配置失败：{e}")
            return None
        finally:
            conn.close()
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        """获取所有 LLM 提供商配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM llm_providers')
            rows = cursor.fetchall()
            return [self._deserialize_provider_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有 LLM 提供商配置失败：{e}")
            return []
        finally:
            conn.close()
    
    def delete_provider(self, name: str) -> bool:
        """删除 LLM 提供商配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM llm_providers WHERE name = ?', (name,))
            conn.commit()
            logger.info(f"删除 LLM 提供商配置：{name}")
            return True
        except Exception as e:
            logger.error(f"删除 LLM 提供商配置失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # ========== 系统配置管理 ==========
    
    def set_system_config(self, key: str, value: str, description: str = None) -> bool:
        """设置系统配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM system_config WHERE key = ?', (key,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE system_config SET
                        value = ?,
                        description = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                ''', (value, description, key))
            else:
                cursor.execute('''
                    INSERT INTO system_config (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, description))
            
            conn.commit()
            logger.info(f"设置系统配置：{key} = {value}")
            return True
        except Exception as e:
            logger.error(f"设置系统配置失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_system_config(self, key: str) -> Optional[str]:
        """获取系统配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT value FROM system_config WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
        except Exception as e:
            logger.error(f"获取系统配置失败：{e}")
            return None
        finally:
            conn.close()
    
    def get_default_provider(self) -> str:
        """获取默认 LLM 提供商"""
        return self.get_system_config('default_provider') or 'eggfans'
    
    def set_default_provider(self, provider: str) -> bool:
        """设置默认 LLM 提供商"""
        return self.set_system_config('default_provider', provider, '默认 LLM 提供商')
    
    # ========== 项目配置管理 ==========
    
    def get_project_config(self) -> Dict[str, Any]:
        """获取项目配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM project_config WHERE id = 1')
            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"获取项目配置失败：{e}")
            return {}
        finally:
            conn.close()
    
    def update_project_config(self, config: Dict[str, Any]) -> bool:
        """更新项目配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE project_config SET
                    project_name = ?,
                    project_path = ?,
                    default_provider = ?,
                    auto_commit = ?,
                    git_author_name = ?,
                    git_author_email = ?,
                    backup_interval = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (
                config.get('project_name', '我的小说'),
                config.get('project_path', './projects/我的小说'),
                config.get('default_provider', 'eggfans'),
                1 if config.get('auto_commit', True) else 0,
                config.get('git_author_name', 'Novel Agent'),
                config.get('git_author_email', 'novel-agent@local'),
                config.get('backup_interval', 24)
            ))
            conn.commit()
            logger.info("项目配置已更新")
            return True
        except Exception as e:
            logger.error(f"更新项目配置失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # ========== 批量导入导出 ==========
    
    def export_config(self) -> Dict[str, Any]:
        """导出所有配置"""
        return {
            'default_provider': self.get_default_provider(),
            'providers': {
                p['name']: p for p in self.get_all_providers()
            },
            'project_config': self.get_project_config(),
            'exported_at': datetime.now().isoformat()
        }
    
    def import_config(self, config: Dict[str, Any]) -> bool:
        """导入配置"""
        try:
            # 设置默认提供商
            if 'default_provider' in config:
                self.set_default_provider(config['default_provider'])
            
            # 导入提供商配置
            if 'providers' in config:
                for name, provider_config in config['providers'].items():
                    self.save_provider(name, provider_config)
            
            # 导入项目配置
            if 'project_config' in config:
                self.update_project_config(config['project_config'])
            
            logger.info("配置导入成功")
            return True
        except Exception as e:
            logger.error(f"配置导入失败：{e}")
            return False


# ========== 全局单例 ==========

_config_db: Optional[ConfigDatabase] = None


def get_config_database() -> ConfigDatabase:
    """获取配置数据库单例"""
    global _config_db
    if _config_db is None:
        _config_db = ConfigDatabase()
    return _config_db


if __name__ == '__main__':
    # 测试
    db = get_config_database()
    
    # 保存测试配置
    db.save_provider('eggfans', {
        'api_format': 'openai',
        'api_key': 'sk-test123',
        'base_url': 'https://eggfans.com',
        'model': 'deepseek-v3.2',
        'timeout': 60
    })
    
    # 设置默认提供商
    db.set_default_provider('eggfans')
    
    # 获取配置
    print("默认提供商:", db.get_default_provider())
    print("所有提供商:", db.get_all_providers())
