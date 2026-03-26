# ==========================================
# 多 Agent 协作小说系统 - 对话专家 Agent
# ==========================================

from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DialogueAgent(BaseAgent):
    """
    对话专家 Agent
    
    职责:
    1. 打磨对话，使其自然流畅
    2. 确保对话个性化（每个人物说话方式不同）
    3. 增加潜台词和言外之意
    4. 控制对话节奏
    5. 通过对话推动情节
    """
    
    def get_system_prompt(self) -> str:
        return """你是一位专业的对话打磨专家，擅长创作自然、生动的对话。

你的原则:
1. **自然真实**: 像真实的人在说话
2. **个性化**: 每个人物有独特的说话方式
3. **有潜台词**: 不要直白，要有言外之意
4. **推动情节**: 对话要有目的
5. **节奏感**: 有快有慢，有张有弛

好的对话是"听其言知其人"。"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get('action')
        
        if action == 'polish_dialogue':
            return await self.polish_dialogue(task)
        elif action == 'write_dialogue':
            return await self.write_dialogue(task)
        elif action == 'add_subtext':
            return await self.add_subtext(task)
        else:
            raise ValueError(f"未知动作：{action}")
    
    async def polish_dialogue(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """打磨对话"""
        dialogue = task.get('dialogue', '')
        characters = task.get('characters', [])
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请打磨以下对话。

## 对话内容
{dialogue}

## 出场人物
{characters}

## 打磨要求
1. 使对话更自然口语化
2. 增加人物个性化
3. 添加潜台词
4. 优化节奏

直接输出打磨后的对话。"""
            
            result = await self.call_llm(prompt, temperature=0.6)
            
            return {
                "status": "success",
                "polished_dialogue": result,
                "word_count": len(result)
            }
        finally:
            self.state = "idle"
    
    async def write_dialogue(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """创作对话"""
        context = task.get('context', '')
        characters = task.get('characters', [])
        purpose = task.get('purpose', '')
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请创作对话。

## 情境
{context}

## 出场人物
{characters}

## 对话目的
{purpose}

请创作自然、有个性化的对话。"""
            
            result = await self.call_llm(prompt, temperature=0.7)
            
            return {
                "status": "success",
                "dialogue": result,
                "character_count": len(characters)
            }
        finally:
            self.state = "idle"
    
    async def add_subtext(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """添加潜台词"""
        dialogue = task.get('dialogue', '')
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请为以下对话添加潜台词。

## 对话
{dialogue}

请在每句对话后标注（潜台词：...）"""
            
            result = await self.call_llm(prompt, temperature=0.5)
            
            return {
                "status": "success",
                "dialogue_with_subtext": result
            }
        finally:
            self.state = "idle"
