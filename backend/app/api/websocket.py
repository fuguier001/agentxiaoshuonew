# ==========================================
# 多 Agent 协作小说系统 - WebSocket 管理
# ==========================================

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket 连接管理器
    """

    _instance: Optional['ConnectionManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._connections: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[str]] = {}
        self._message_handlers: Dict[str, Callable] = {}
        logger.info("WebSocket 连接管理器初始化完成")

    async def connect(self, websocket: Any, client_id: str):
        """建立连接"""
        self._connections[client_id] = websocket
        logger.info(f"WebSocket 连接建立：{client_id}")

    async def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self._connections:
            del self._connections[client_id]
            for topic in self._subscribers:
                if client_id in self._subscribers[topic]:
                    self._subscribers[topic].remove(client_id)
            logger.info(f"WebSocket 连接断开：{client_id}")

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """发送个人消息"""
        if client_id in self._connections:
            try:
                websocket = self._connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败：{e}")
                await self.disconnect(client_id)

    async def broadcast(self, message: Dict[str, Any], topic: str = "global"):
        """广播消息到所有订阅者"""
        if topic in self._subscribers:
            disconnected = []
            for client_id in self._subscribers[topic]:
                try:
                    if client_id in self._connections:
                        await self._connections[client_id].send_json(message)
                    else:
                        disconnected.append(client_id)
                except Exception as e:
                    logger.error(f"广播消息失败：{e}")
                    disconnected.append(client_id)

            for client_id in disconnected:
                await self.disconnect(client_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """广播到所有连接"""
        disconnected = []
        for client_id, websocket in self._connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败：{e}")
                disconnected.append(client_id)

        for client_id in disconnected:
            await self.disconnect(client_id)

    def subscribe(self, client_id: str, topic: str):
        """订阅主题"""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        if client_id not in self._subscribers[topic]:
            self._subscribers[topic].append(client_id)
            logger.info(f"客户端 {client_id} 订阅了主题 {topic}")

    def unsubscribe(self, client_id: str, topic: str):
        """取消订阅"""
        if topic in self._subscribers and client_id in self._subscribers[topic]:
            self._subscribers[topic].remove(client_id)
            logger.info(f"客户端 {client_id} 取消订阅了主题 {topic}")

    def register_handler(self, event_type: str, handler: Callable):
        """注册消息处理器"""
        self._message_handlers[event_type] = handler

    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """处理收到的消息"""
        event_type = message.get('type')
        if event_type in self._message_handlers:
            handler = self._message_handlers[event_type]
            try:
                await handler(client_id, message.get('data', {}))
            except Exception as e:
                logger.error(f"处理消息失败：{e}")
        else:
            logger.warning(f"未知消息类型：{event_type}")

    def get_connection_count(self) -> int:
        """获取连接数"""
        return len(self._connections)

    def get_subscriber_count(self, topic: str = "global") -> int:
        """获取订阅者数量"""
        return len(self._subscribers.get(topic, []))


class AgentStatusBroadcaster:
    """
    Agent 状态广播器
    """

    def __init__(self):
        self._manager = ConnectionManager()
        self._last_status: Dict[str, Dict[str, Any]] = {}

    async def broadcast_agent_status(self, agent_id: str, status: Dict[str, Any]):
        """广播 Agent 状态"""
        message = {
            'type': 'agent_status',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'agent_id': agent_id,
                'status': status
            }
        }
        self._last_status[agent_id] = status
        await self._manager.broadcast(message, topic='agents')
        await self._manager.broadcast(message, topic='global')

    async def broadcast_task_progress(self, task_id: str, progress: int, stage: str):
        """广播任务进度"""
        message = {
            'type': 'task_progress',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'task_id': task_id,
                'progress': progress,
                'stage': stage
            }
        }
        await self._manager.broadcast(message, topic='tasks')
        await self._manager.broadcast(message, topic='global')

    async def broadcast_log(self, level: str, message: str, agent_id: str = None):
        """广播日志消息"""
        message_data = {
            'type': 'log',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'level': level,
                'message': message,
                'agent_id': agent_id
            }
        }
        await self._manager.broadcast(message_data, topic='logs')

    async def broadcast_chapter_created(self, novel_id: str, chapter_num: int, title: str):
        """广播章节创建"""
        message = {
            'type': 'chapter_created',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'novel_id': novel_id,
                'chapter_num': chapter_num,
                'title': title
            }
        }
        await self._manager.broadcast(message, topic='chapters')

    async def broadcast_learning_complete(self, analysis_id: str, author: str, title: str):
        """广播学习完成"""
        message = {
            'type': 'learning_complete',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'analysis_id': analysis_id,
                'author': author,
                'title': title
            }
        }
        await self._manager.broadcast(message, topic='learning')

    def get_last_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 最后状态"""
        return self._last_status.get(agent_id)

    def get_all_last_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有 Agent 最后状态"""
        return self._last_status.copy()


_connection_manager: Optional[ConnectionManager] = None
_agent_broadcaster: Optional[AgentStatusBroadcaster] = None


def get_connection_manager() -> ConnectionManager:
    """获取连接管理器单例"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_agent_broadcaster() -> AgentStatusBroadcaster:
    """获取广播器单例"""
    global _agent_broadcaster
    if _agent_broadcaster is None:
        _agent_broadcaster = AgentStatusBroadcaster()
    return _agent_broadcaster