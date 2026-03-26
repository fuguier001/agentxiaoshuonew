# ==========================================
# 多 Agent 协作小说系统 - 审核编辑 Agent
# ==========================================

from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """
    审核编辑 Agent
    
    职责:
    1. 检查内容一致性（人物、情节、设定）
    2. 发现逻辑漏洞
    3. 检查文字错误
    4. 评估整体质量
    """
    
    def get_system_prompt(self) -> str:
        return """你是一位细致的审核编辑，负责检查作品的一致性和逻辑性。

你的检查清单:
1. **人物一致性**: 不 OOC
2. **情节连贯性**: 时间线、因果关系
3. **设定一致性**: 世界观、规则
4. **文字错误**: 错别字、标点、语句
5. **逻辑漏洞**: 不合理之处

你以严谨著称，不放过任何细节。"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get('action')
        
        if action == 'consistency_check':
            return await self.consistency_check(task)
        elif action == 'logic_check':
            return await self.logic_check(task)
        elif action == 'proofread':
            return await self.proofread(task)
        else:
            raise ValueError(f"未知动作：{action}")
    
    async def consistency_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """一致性检查"""
        content = task.get('content', '')
        context = task.get('context', {})
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请检查以下内容的一致性。

## 内容
{content[:8000]}

## 上下文
{context}

## 检查维度
1. 人物一致性（性格、行为、对话）
2. 情节连贯性（时间线、因果）
3. 设定一致性（世界观、规则）

## 输出格式
{{
    "consistent": true/false,
    "issues": [
        {{"type": "character/plot/setting", "description": "...", "severity": "low/medium/high"}}
    ]
}}"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            check = self._parse_json(result)
            
            return {
                "status": "success",
                "consistent": check.get('consistent', True),
                "issues": check.get('issues', [])
            }
        finally:
            self.state = "idle"
    
    async def logic_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """逻辑检查"""
        content = task.get('content', '')
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请检查以下内容的逻辑漏洞。

## 内容
{content[:8000]}

找出所有不合理、不成立、矛盾的地方。"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            
            return {
                "status": "success",
                "logic_issues": result
            }
        finally:
            self.state = "idle"
    
    async def proofread(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """校对文字"""
        content = task.get('content', '')
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请校对以下文字。

## 内容
{content[:8000]}

找出错别字、标点错误、语句不通的地方。"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            
            return {
                "status": "success",
                "proofread_result": result
            }
        finally:
            self.state = "idle"
    
    def _parse_json(self, text: str) -> Dict:
        import json
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        return {}
