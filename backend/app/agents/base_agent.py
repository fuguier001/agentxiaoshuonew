# ==========================================
# 多 Agent 协作小说系统 - Base Agent
# 所有 Agent 的基类
# ==========================================

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import httpx
import asyncio

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Agent 基类

    所有 7 大 Agent 都继承此类：
    - LearningAgent (学习分析师)
    - WriterAgent (章节写手)
    - PlotAgent (剧情架构师)
    - CharacterAgent (人物设计师)
    - DialogueAgent (对话专家)
    - ReviewerAgent (审核编辑)
    - EditorAgent (主编)
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.llm_client = config.get('llm_client')
        self.memory_engine = config.get('memory_engine')
        self.state = "idle"
        self.last_active: Optional[datetime] = None

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务（子类必须实现）"""
        raise NotImplementedError("子类必须实现 execute 方法")

    def get_system_prompt(self) -> str:
        """获取 Agent 的系统提示词（子类必须实现）"""
        raise NotImplementedError("子类必须实现 get_system_prompt 方法")

    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        调用 LLM 生成内容

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（默认使用 Agent 的系统提示词）
            temperature: 生成温度
            max_tokens: 最大 token 数

        Returns:
            生成的文本内容
        """
        if not self.llm_client:
            raise Exception("LLM 客户端未配置")

        # 如果没有指定系统提示词，使用 Agent 的默认提示词
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # 处理 llm_client 的不同类型
        if isinstance(self.llm_client, dict):
            # 旧格式：字典形式
            api_key = self.llm_client.get('api_key', '')
            base_url = self.llm_client.get('base_url', '')
            model = self.llm_client.get('model', '')
            timeout = self.llm_client.get('timeout', 300)
            endpoint = self.llm_client.get('endpoint', '/v1/chat/completions')

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': max_tokens,
                'temperature': temperature
            }

            # 重试机制
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(
                            f"{base_url}{endpoint}",
                            headers=headers,
                            json=payload
                        )

                        if response.status_code == 200:
                            data = response.json()
                            content = data['choices'][0]['message']['content']
                            logger.info(f"[{self.agent_id}] LLM 调用成功，返回 {len(content)} 字")
                            return content
                        else:
                            error_msg = f"LLM API 调用失败：{response.status_code}"
                            logger.error(f"[{self.agent_id}] {error_msg}")
                            if attempt < 2:
                                await asyncio.sleep(3)
                            else:
                                raise Exception(error_msg)
                except httpx.ReadError as e:
                    logger.error(f"[{self.agent_id}] 网络读取错误: {e}")
                    if attempt < 2:
                        await asyncio.sleep(3)
                    else:
                        raise
                except Exception as e:
                    logger.error(f"[{self.agent_id}] LLM 调用异常: {e}")
                    if attempt < 2:
                        await asyncio.sleep(3)
                    else:
                        raise

            raise Exception("LLM 调用失败，已达最大重试次数")

        else:
            # 新格式：LLMClient 对象
            return await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def update_state(self, new_state: str):
        """更新 Agent 状态"""
        self.state = new_state
        self.last_active = datetime.now()
        logger.info(f"[{self.agent_id}] 状态更新：{new_state}")

    def get_status(self) -> Dict[str, Any]:
        """获取 Agent 状态信息"""
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "config_summary": self._get_config_summary()
        }

    def _get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要（脱敏）"""
        summary = {}
        for key, value in self.config.items():
            if isinstance(value, str) and 'key' in key.lower():
                summary[key] = '***' + value[-4:] if value else ''
            elif key in ['llm_client', 'memory_engine']:
                summary[key] = 'configured' if value else 'not_configured'
            else:
                summary[key] = value
        return summary
