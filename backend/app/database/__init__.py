# ==========================================
# 多 Agent 协作小说系统 - 数据库模块
# ==========================================

from .learning_db import get_learning_database, LearningDatabase
from .school_db import get_school_database, SchoolDatabase

__all__ = [
    'get_learning_database',
    'LearningDatabase',
    'get_school_database',
    'SchoolDatabase'
]