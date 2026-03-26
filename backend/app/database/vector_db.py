# ==========================================
# 多 Agent 协作小说系统 - 向量数据库管理
# ==========================================

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    向量数据库 - 使用 Chroma 实现语义搜索
    """

    _instance: Optional['VectorDatabase'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._storage_path = Path("./data/vector_db")
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._chroma_client = None
        self._collections: Dict[str, Any] = {}
        self._text_index_file = self._storage_path / "text_index.json"
        self._text_index: Dict[str, Dict[str, Any]] = {}
        self._load_text_index()
        self._init_chroma()
        logger.info("向量数据库初始化完成")

    def _load_text_index(self):
        """加载文本索引"""
        if self._text_index_file.exists():
            try:
                with open(self._text_index_file, 'r', encoding='utf-8') as f:
                    self._text_index = json.load(f)
                logger.info(f"加载了 {len(self._text_index)} 条文本索引")
            except Exception as e:
                logger.error(f"加载文本索引失败：{e}")
                self._text_index = {}

    def _save_text_index(self):
        """保存文本索引"""
        try:
            with open(self._text_index_file, 'w', encoding='utf-8') as f:
                json.dump(self._text_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存文本索引失败：{e}")

    def _init_chroma(self):
        """初始化 Chroma"""
        try:
            import chromadb
            from chromadb.config import Settings

            self._chroma_client = chromadb.Client(Settings(
                persist_directory=str(self._storage_path / "chroma_db"),
                anonymized_telemetry=False
            ))
            logger.info("Chroma 向量数据库初始化成功")
        except ImportError:
            logger.warning("Chroma 未安装，将使用简单的文本搜索作为后备方案")
            self._chroma_client = None
        except Exception as e:
            logger.warning(f"Chroma 初始化失败：{e}，将使用简单的文本搜索作为后备方案")
            self._chroma_client = None

    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量（简化实现）"""
        import hashlib
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        vector = []
        for i in range(1536):
            vector.append(((hash_value >> i) & 1) * 0.5 + 0.25)
        norm = sum(v * v for v in vector) ** 0.5
        return [v / norm for v in vector]

    def _get_collection_name(self, collection_type: str) -> str:
        """获取集合名称"""
        return f"novel_agent_{collection_type}"

    async def add_text(
        self,
        collection_type: str,
        text_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """添加文本到向量数据库"""
        try:
            if self._chroma_client:
                collection_name = self._get_collection_name(collection_type)
                try:
                    collection = self._chroma_client.get_collection(collection_name)
                except:
                    collection = self._chroma_client.create_collection(collection_name)

                embedding = self._get_text_embedding(content)
                collection.add(
                    ids=[text_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata or {}]
                )
            else:
                pass

            self._text_index[text_id] = {
                'id': text_id,
                'content': content,
                'metadata': metadata or {},
                'collection_type': collection_type,
                'created_at': datetime.now().isoformat()
            }
            self._save_text_index()

            logger.info(f"添加文本到向量数据库：{text_id}")
            return True

        except Exception as e:
            logger.error(f"添加文本失败：{e}")
            return False

    async def search(
        self,
        collection_type: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """语义搜索"""
        try:
            if self._chroma_client:
                collection_name = self._get_collection_name(collection_type)
                try:
                    collection = self._chroma_client.get_collection(collection_name)
                except:
                    return []

                query_embedding = self._get_text_embedding(query)
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )

                search_results = []
                if results and results.get('ids') and results['ids']:
                    for i, doc_id in enumerate(results['ids'][0]):
                        search_results.append({
                            'id': doc_id,
                            'content': results['documents'][0][i] if results.get('documents') else '',
                            'distance': results.get('distances', [[]])[0][i] if results.get('distances') else 0,
                            'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {}
                        })
                return search_results
            else:
                return self._simple_text_search(collection_type, query, top_k)

        except Exception as e:
            logger.error(f"语义搜索失败：{e}")
            return self._simple_text_search(collection_type, query, top_k)

    def _simple_text_search(
        self,
        collection_type: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """简单的文本搜索（后备方案）"""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_results = []
        for text_id, data in self._text_index.items():
            if data.get('collection_type') != collection_type:
                continue

            content_lower = data.get('content', '').lower()

            score = 0
            for word in query_words:
                if word in content_lower:
                    score += 1

            if query_lower in content_lower:
                score += 10

            if score > 0:
                scored_results.append({
                    'id': text_id,
                    'content': data.get('content', ''),
                    'distance': 1.0 / (score + 1),
                    'metadata': data.get('metadata', {}),
                    'score': score
                })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]

    async def delete_text(self, text_id: str) -> bool:
        """删除文本"""
        try:
            if text_id in self._text_index:
                del self._text_index[text_id]
                self._save_text_index()
                logger.info(f"从索引中删除文本：{text_id}")
            return True
        except Exception as e:
            logger.error(f"删除文本失败：{e}")
            return False

    async def get_text(self, text_id: str) -> Optional[Dict[str, Any]]:
        """获取文本"""
        return self._text_index.get(text_id)

    async def get_collection_stats(self, collection_type: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        count = sum(1 for data in self._text_index.values()
                    if data.get('collection_type') == collection_type)
        return {
            'collection_type': collection_type,
            'document_count': count,
            'storage_path': str(self._storage_path)
        }


_vector_db: Optional[VectorDatabase] = None


def get_vector_database() -> VectorDatabase:
    """获取向量数据库单例"""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase()
    return _vector_db