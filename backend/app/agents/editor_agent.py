# ==========================================
# 多 Agent 协作小说系统 - 主编 Agent
# ==========================================

from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent):
    """
    主编 Agent
    
    职责:
    1. 最终审核章节质量
    2. 确保风格统一
    3. 把关整体方向
    4. 决策是否通过
    """
    
    def get_system_prompt(self) -> str:
        return """你是一位经验丰富的文学主编，负责小说项目的整体把控和最终审核。

你的职责:
1. 审核章节质量，确保符合项目风格
2. 检查情节连贯性，发现逻辑漏洞
3. 评估人物塑造，防止 OOC
4. 给出修改建议，提升作品质量
5. 决策章节是否通过

你专业严谨，有卓越的审美判断力。"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get('action')
        
        if action == 'final_review':
            return await self.final_review(task)
        elif action == 'quality_assessment':
            return await self.quality_assessment(task)
        elif action == 'style_check':
            return await self.style_check(task)
        else:
            raise ValueError(f"未知动作：{action}")
    
    async def final_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """最终审核"""
        chapter_content = task.get('content', '')
        chapter_num = task.get('chapter_num')
        reviews = task.get('reviews', {})  # 其他 Agent 的审核结果
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请对以下章节进行最终审核。

## 章节信息
- 章节号：第{chapter_num}章

## 章节内容
{chapter_content[:8000]}

## 其他审核意见
{reviews}

## 审核维度
1. **风格一致性** (1-10 分)
2. **情节连贯性** (1-10 分)
3. **人物塑造** (1-10 分)
4. **对话质量** (1-10 分)
5. **描写效果** (1-10 分)
6. **节奏控制** (1-10 分)

## 输出格式
{{
    "overall_score": 8.5,
    "dimension_scores": {{
        "style_consistency": 9,
        "plot_coherence": 8,
        "character_development": 9,
        "dialogue_quality": 8,
        "description_quality": 9,
        "pacing": 8
    }},
    "strengths": ["优点 1", "优点 2"],
    "weaknesses": ["问题 1", "问题 2"],
    "verdict": "pass/review/revise",
    "comments": "总体评价",
    "required_revisions": ["必须修改的问题"]
}}"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            review = self._parse_json(result)
            
            return {
                "status": "success",
                "chapter_num": chapter_num,
                "review": review,
                "verdict": review.get('verdict', 'review'),
                "overall_score": review.get('overall_score', 0)
            }
        finally:
            self.state = "idle"
    
    async def quality_assessment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """质量评估"""
        content = task.get('content', '')
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请评估以下内容的整体质量。

## 内容
{content[:8000]}

请给出 1-10 分的评分和详细评价。"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            
            return {
                "status": "success",
                "assessment": result
            }
        finally:
            self.state = "idle"
    
    async def style_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """风格检查"""
        content = task.get('content', '')
        target_style = task.get('target_style', {})
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请检查内容是否符合目标风格。

## 内容
{content[:8000]}

## 目标风格
{target_style}

请评估风格匹配度。"""
            
            result = await self.call_llm(prompt, temperature=0.3)
            
            return {
                "status": "success",
                "style_match": result
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
