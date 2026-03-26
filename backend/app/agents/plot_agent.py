# ==========================================
# 多 Agent 协作小说系统 - 剧情架构师 Agent
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PlotAgent(BaseAgent):
    """
    剧情架构师 Agent
    
    职责:
    1. 设计情节结构（三幕式、多线叙事等）
    2. 细化章节大纲
    3. 埋设和回收伏笔
    4. 控制叙事节奏
    5. 设计情节转折
    """
    
    def get_system_prompt(self) -> str:
        return """你是一位专业的剧情架构师，擅长设计引人入胜的故事情节。

你的专长:
1. **三幕式结构**: 建制→对抗→解决
2. **多线叙事**: 主线 + 支线交织
3. **悬念设计**: 钩子、转折、反转
4. **节奏控制**: 张弛有度，高潮迭起
5. **伏笔管理**: 埋设、呼应、回收

请确保情节逻辑自洽，转折合理，节奏恰当。"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行剧情任务"""
        action = task.get('action')
        
        if action == 'refine_chapter_outline':
            return await self.refine_chapter_outline(task)
        elif action == 'design_plot_structure':
            return await self.design_plot_structure(task)
        elif action == 'setup_plot_hooks':
            return await self.setup_plot_hooks(task)
        elif action == 'check_plot_consistency':
            return await self.check_plot_consistency(task)
        elif action == 'design_plot_twist':
            return await self.design_plot_twist(task)
        else:
            raise ValueError(f"未知动作：{action}")
    
    async def refine_chapter_outline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        细化章节大纲
        
        输入:
        {
            "chapter_num": 5,
            "outline": "主角首次遭遇反派",
            "previous_chapters": [...],
            "plot_threads": [...]
        }
        
        输出:
        {
            "status": "success",
            "chapter_num": 5,
            "refined_outline": {
                "opening": "...",
                "development": "...",
                "climax": "...",
                "ending": "..."
            },
            "plot_points": [...],
            "hooks_setup": [...],
            "hooks_resolved": [...]
        }
        """
        chapter_num = task.get('chapter_num')
        outline = task.get('outline', '')
        previous_chapters = task.get('previous_chapters', [])
        plot_threads = task.get('plot_threads', [])
        
        logger.info(f"细化第{chapter_num}章大纲")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = self._build_refine_outline_prompt(
                chapter_num, outline, previous_chapters, plot_threads
            )
            
            result = await self.call_llm(prompt, temperature=0.5)
            refined = self._parse_json(result)
            
            return {
                "status": "success",
                "chapter_num": chapter_num,
                "refined_outline": refined,
                "plot_points": refined.get('plot_points', []),
                "hooks_setup": refined.get('hooks_setup', []),
                "hooks_resolved": refined.get('hooks_resolved', [])
            }
        
        except Exception as e:
            logger.error(f"大纲细化失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "大纲细化失败"
            }
        
        finally:
            self.state = "idle"
    
    async def design_plot_structure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        设计整体情节结构
        
        输入:
        {
            "story_concept": "现代都市修仙",
            "total_chapters": 100,
            "main_characters": [...],
            "themes": ["成长", "友情", "正义"]
        }
        
        输出:
        {
            "status": "success",
            "structure": {
                "act1": {"chapters": "1-30", "description": "..."},
                "act2": {"chapters": "31-70", "description": "..."},
                "act3": {"chapters": "71-100", "description": "..."}
            },
            "major_turning_points": [...],
            "sub_plots": [...]
        }
        """
        story_concept = task.get('story_concept', '')
        total_chapters = task.get('total_chapters', 100)
        main_characters = task.get('main_characters', [])
        themes = task.get('themes', [])
        
        logger.info(f"设计情节结构：{story_concept}")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = self._build_structure_design_prompt(
                story_concept, total_chapters, main_characters, themes
            )
            
            result = await self.call_llm(prompt, temperature=0.4)
            structure = self._parse_json(result)
            
            return {
                "status": "success",
                "structure": structure,
                "act_count": structure.get('act_count', 3),
                "turning_points": structure.get('turning_points', [])
            }
        
        except Exception as e:
            logger.error(f"情节结构设计失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "情节结构设计失败"
            }
        
        finally:
            self.state = "idle"
    
    async def setup_plot_hooks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        设计伏笔
        
        输入:
        {
            "chapter_num": 5,
            "context": "当前情节",
            "hook_type": "foreshadowing/mystery/question/promise/threat"
        }
        
        输出:
        {
            "status": "success",
            "hooks": [
                {
                    "hook_id": "hook_001",
                    "type": "foreshadowing",
                    "description": "伏笔描述",
                    "importance": 8,
                    "expected_resolution_chapter": 15
                }
            ]
        }
        """
        chapter_num = task.get('chapter_num')
        context = task.get('context', '')
        hook_type = task.get('hook_type', 'foreshadowing')
        
        logger.info(f"设计伏笔：{hook_type}")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = self._build_hook_design_prompt(chapter_num, context, hook_type)
            
            result = await self.call_llm(prompt, temperature=0.5)
            hooks = self._parse_json_list(result)
            
            return {
                "status": "success",
                "hooks": hooks,
                "hook_count": len(hooks)
            }
        
        except Exception as e:
            logger.error(f"伏笔设计失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "伏笔设计失败"
            }
        
        finally:
            self.state = "idle"
    
    async def check_plot_consistency(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查情节一致性
        
        输入:
        {
            "chapter_content": "章节内容",
            "previous_plot": "之前情节",
            "character_arcs": {...}
        }
        
        输出:
        {
            "status": "success",
            "consistent": true/false,
            "issues": [
                {
                    "type": "timeline/character/logic",
                    "description": "问题描述",
                    "severity": "low/medium/high"
                }
            ]
        }
        """
        chapter_content = task.get('chapter_content', '')
        previous_plot = task.get('previous_plot', '')
        character_arcs = task.get('character_arcs', {})
        
        logger.info("检查情节一致性")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = self._build_consistency_check_prompt(
                chapter_content, previous_plot, character_arcs
            )
            
            result = await self.call_llm(prompt, temperature=0.3)
            check_result = self._parse_json(result)
            
            return {
                "status": "success",
                "consistent": check_result.get('consistent', True),
                "issues": check_result.get('issues', []),
                "suggestions": check_result.get('suggestions', [])
            }
        
        except Exception as e:
            logger.error(f"情节一致性检查失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "情节一致性检查失败"
            }
        
        finally:
            self.state = "idle"
    
    async def design_plot_twist(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        设计情节转折
        
        输入:
        {
            "current_situation": "当前情况",
            "twist_type": "revelation/betrayal/reversal/surprise",
            "surprise_level": "low/medium/high"
        }
        
        输出:
        {
            "status": "success",
            "twist": {
                "type": "revelation",
                "description": "转折描述",
                "setup_required": ["需要铺垫 1", "需要铺垫 2"],
                "impact": "影响描述"
            }
        }
        """
        current_situation = task.get('current_situation', '')
        twist_type = task.get('twist_type', 'reversal')
        surprise_level = task.get('surprise_level', 'medium')
        
        logger.info(f"设计情节转折：{twist_type}")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = self._build_twist_design_prompt(
                current_situation, twist_type, surprise_level
            )
            
            result = await self.call_llm(prompt, temperature=0.6)
            twist = self._parse_json(result)
            
            return {
                "status": "success",
                "twist": twist,
                "surprise_level": surprise_level
            }
        
        except Exception as e:
            logger.error(f"情节转折设计失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "情节转折设计失败"
            }
        
        finally:
            self.state = "idle"
    
    # ========== 辅助方法 ==========
    
    def _build_refine_outline_prompt(
        self,
        chapter_num: int,
        outline: str,
        previous_chapters: List[Dict],
        plot_threads: List[Dict]
    ) -> str:
        """构建大纲细化 Prompt"""
        
        prev_summary = "\n".join([
            f"- 第{ch.get('num', '?')}章：{ch.get('summary', '无')}"
            for ch in previous_chapters[-3:]  # 最近 3 章
        ])
        
        thread_status = "\n".join([
            f"- {t.get('name', '线索')}: {t.get('status', 'open')} (重要度：{t.get('priority', 5)})"
            for t in plot_threads
        ])
        
        return f"""请细化以下章节大纲。

## 章节信息
- 章节号：第{chapter_num}章
- 简单大纲：{outline}

## 前情提要（最近 3 章）
{prev_summary}

## 当前情节线索状态
{thread_status}

## 细化要求
请将大纲细化为以下结构：

1. **开篇** (10-15%): 如何开始本章，吸引读者
2. **发展** (40-50%): 情节如何推进，人物如何行动
3. **高潮** (25-30%): 本章的高潮点是什么
4. **结尾** (10-15%): 如何结尾，留下什么悬念

## 输出格式
{{
    "opening": "开篇描述（100-200 字）",
    "development": "发展描述（200-300 字）",
    "climax": "高潮描述（150-200 字）",
    "ending": "结尾描述（100-150 字）",
    "plot_points": [
        {{"point": "情节点 1", "purpose": "目的"}},
        {{"point": "情节点 2", "purpose": "目的"}}
    ],
    "hooks_setup": [
        {{"hook": "伏笔描述", "type": "类型", "importance": 5}}
    ],
    "hooks_resolved": [
        {{"hook_id": "伏笔 ID", "resolution": "回收方式"}}
    ],
    "character_focus": ["重点人物 1", "重点人物 2"],
    "estimated_word_count": 3000
}}

请确保情节连贯，与前文呼应，伏笔合理。"""
    
    def _build_structure_design_prompt(
        self,
        story_concept: str,
        total_chapters: int,
        main_characters: List[Dict],
        themes: List[str]
    ) -> str:
        """构建结构设计 Prompt"""
        return f"""请设计整体情节结构。

## 故事概念
{story_concept}

## 总章节数
{total_chapters}章

## 主要人物
{[c.get('name', '') for c in main_characters]}

## 主题
{', '.join(themes)}

## 设计要求
请使用三幕式结构设计：

**第一幕（建制）**: 介绍世界观、人物、初始情境
**第二幕（对抗）**: 冲突升级、人物成长、多次转折
**第三幕（解决）**: 高潮对决、问题解决、结局

## 输出格式
{{
    "act_count": 3,
    "act1": {{
        "chapters": "1-{int(total_chapters*0.3)}",
        "title": "建制",
        "description": "第一幕描述（200-300 字）",
        "key_events": ["事件 1", "事件 2", "事件 3"],
        "ending_point": "第一幕结束点"
    }},
    "act2": {{
        "chapters": "{int(total_chapters*0.3)+1}-{int(total_chapters*0.7)}",
        "title": "对抗",
        "description": "第二幕描述（200-300 字）",
        "key_events": ["事件 1", "事件 2", "事件 3", "事件 4"],
        "midpoint": "中点转折",
        "ending_point": "第二幕结束点"
    }},
    "act3": {{
        "chapters": "{int(total_chapters*0.7)+1}-{total_chapters}",
        "title": "解决",
        "description": "第三幕描述（200-300 字）",
        "key_events": ["事件 1", "事件 2", "事件 3"],
        "climax": "最终高潮",
        "resolution": "结局"
    }},
    "major_turning_points": [
        {{"chapter": 1, "event": "激励事件"}},
        {{"chapter": 30, "event": "第一幕转折"}},
        {{"chapter": 50, "event": "中点转折"}},
        {{"chapter": 70, "event": "第二幕转折"}},
        {{"chapter": 95, "event": "最终高潮"}}
    ],
    "sub_plots": [
        {{"name": "支线 1", "description": "描述", "related_characters": []}},
        {{"name": "支线 2", "description": "描述", "related_characters": []}}
    ]
}}

请确保结构完整，节奏合理，高潮迭起。"""
    
    def _build_hook_design_prompt(
        self,
        chapter_num: int,
        context: str,
        hook_type: str
    ) -> str:
        """构建伏笔设计 Prompt"""
        return f"""请设计伏笔。

## 章节信息
- 章节号：第{chapter_num}章
- 当前情境：{context}
- 伏笔类型：{hook_type}

## 伏笔类型说明
- **foreshadowing**: 预示未来事件
- **mystery**: 制造悬念疑问
- **question**: 提出问题
- **promise**: 暗示承诺或目标
- **threat**: 暗示危险或威胁

## 设计要求
请设计 2-3 个伏笔，要求：
1. 自然融入当前情节
2. 不显得刻意
3. 有明确的预期回收章节
4. 重要度合理（1-10）

## 输出格式
[
    {{
        "hook_id": "hook_{chapter_num}_001",
        "type": "{hook_type}",
        "description": "伏笔描述（50-100 字）",
        "how_to_plant": "如何埋设（具体写法）",
        "importance": 7,
        "expected_resolution_chapter": {chapter_num + 10},
        "related_characters": ["相关人物"],
        "hints": ["可以给出的暗示"]
    }}
]

请确保伏笔自然、有吸引力。"""
    
    def _build_consistency_check_prompt(
        self,
        chapter_content: str,
        previous_plot: str,
        character_arcs: Dict
    ) -> str:
        """构建一致性检查 Prompt"""
        return f"""请检查情节一致性。

## 当前章节内容
{chapter_content[:8000]}

## 之前情节摘要
{previous_plot[:2000]}

## 人物弧线
{character_arcs}

## 检查维度
1. **时间线**: 时间顺序是否正确
2. **人物一致性**: 人物行为是否符合设定
3. **情节逻辑**: 因果关系是否成立
4. **设定一致性**: 世界观设定是否矛盾
5. **伏笔呼应**: 是否有未解释的伏笔

## 输出格式
{{
    "consistent": true/false,
    "issues": [
        {{
            "type": "timeline/character/logic/setting/hook",
            "description": "问题描述",
            "severity": "low/medium/high",
            "location": "问题位置",
            "suggestion": "修改建议"
        }}
    ],
    "suggestions": ["总体建议 1", "总体建议 2"]
}}

请仔细检查，发现所有潜在问题。"""
    
    def _build_twist_design_prompt(
        self,
        current_situation: str,
        twist_type: str,
        surprise_level: str
    ) -> str:
        """构建转折设计 Prompt"""
        return f"""请设计情节转折。

## 当前情况
{current_situation}

## 转折类型
- **revelation**: 真相揭露
- **betrayal**: 背叛
- **reversal**: 形势逆转
- **surprise**: 意外事件

选择：{twist_type}

## 惊喜程度
- **low**: 轻微转折，读者可猜到
- **medium**: 中等转折，部分读者意外
- **high**: 重大转折，大多数读者意外

选择：{surprise_level}

## 设计要求
1. 转折要合理，有铺垫
2. 符合人物动机
3. 推动情节发展
4. 有情感冲击

## 输出格式
{{
    "type": "{twist_type}",
    "description": "转折描述（100-200 字）",
    "setup_required": [
        "需要提前铺垫 1",
        "需要提前铺垫 2",
        "需要提前铺垫 3"
    ],
    "impact": "对情节的影响",
    "character_reactions": [
        {{"character": "人物 A", "reaction": "反应"}}
    ],
    "follow_up": "转折后的发展"
}}

请设计一个合理且有冲击力的转折。"""
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """解析 JSON 结果"""
        import json
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            logger.warning(f"JSON 解析失败：{e}")
        return None
    
    def _parse_json_list(self, text: str) -> List[Dict]:
        """解析 JSON 列表结果"""
        import json
        try:
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            logger.warning(f"JSON 列表解析失败：{e}")
        return []
