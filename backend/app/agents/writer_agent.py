# ==========================================
# 多 Agent 协作小说系统 - 章节写手 Agent
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """
    章节写手 Agent
    
    职责:
    1. 根据大纲撰写章节
    2. 应用学到的风格和技巧
    3. 保持人物和情节连贯性
    4. 创造有画面感的场景
    """
    
    def get_system_prompt(self) -> str:
        return """你是一位专业的小说作家，擅长创作引人入胜的故事。

你的写作原则:
1. **开篇吸引**: 第一段就要抓住读者注意力
2. **场景描写**: 调动五感，创造沉浸式体验
3. **对话自然**: 符合人物身份，推动情节发展
4. **节奏控制**: 张弛有度，避免平铺直叙
5. **细节真实**: 具体细节胜过抽象描述

请遵循项目设定的写作风格，保持人物不 OOC，情节连贯。"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行写作任务"""
        action = task.get('action')
        
        if action == 'write_chapter':
            return await self.write_chapter(task)
        elif action == 'write_scene':
            return await self.write_scene(task)
        elif action == 'continue_chapter':
            return await self.continue_chapter(task)
        elif action == 'revise_chapter':
            return await self.revise_chapter(task)
        else:
            raise ValueError(f"未知动作：{action}")
    
    async def write_chapter(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        撰写完整章节
        
        输入:
        {
            "chapter_num": 5,
            "title": "章节标题",
            "outline": "章节大纲",
            "word_count_target": 3000,
            "style_context": {...},
            "memory_context": {...}
        }
        
        输出:
        {
            "status": "success",
            "chapter_num": 5,
            "content": "章节内容",
            "word_count": 3245,
            "style_applied": {...},
            "techniques_used": [...]
        }
        """
        chapter_num = task.get('chapter_num')
        title = task.get('title', f'第{chapter_num}章')
        outline = task.get('outline', '')
        word_count_target = task.get('word_count_target', 3000)
        style_context = task.get('style_context', {})
        memory_context = task.get('memory_context', {})
        
        logger.info(f"开始撰写第{chapter_num}章：{title}")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            # 构建写作 Prompt
            prompt = self._build_chapter_prompt(
                chapter_num=chapter_num,
                title=title,
                outline=outline,
                word_count=word_count_target,
                style_context=style_context,
                memory_context=memory_context
            )
            
            # 调用 LLM 生成章节
            content = await self.call_llm(
                prompt,
                temperature=0.7,  # 较高温度增加创意
                max_tokens=word_count_target * 2  # 预留足够空间
            )
            
            # 统计字数
            word_count = len(content)
            
            logger.info(f"章节撰写完成：{word_count}字")
            
            return {
                "status": "success",
                "chapter_num": chapter_num,
                "title": title,
                "content": content,
                "word_count": word_count,
                "style_applied": style_context.get('style_name', 'default'),
                "techniques_used": memory_context.get('techniques', [])
            }
        
        except Exception as e:
            logger.error(f"章节撰写失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "章节撰写失败"
            }
        
        finally:
            self.state = "idle"
    
    async def write_scene(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        撰写特定场景
        
        输入:
        {
            "scene_type": "opening/climax/transition/ending",
            "scene_description": "场景描述",
            "characters": ["角色 1", "角色 2"],
            "emotion": "tense/romantic/sad/exciting",
            "technique_id": "可选：指定使用的技巧"
        }
        
        输出:
        {
            "status": "success",
            "scene_type": "opening",
            "content": "场景内容",
            "word_count": 500
        }
        """
        scene_type = task.get('scene_type', 'normal')
        scene_description = task.get('scene_description', '')
        characters = task.get('characters', [])
        emotion = task.get('emotion', 'neutral')
        technique_id = task.get('technique_id')
        
        logger.info(f"开始撰写场景：{scene_type}")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            # 获取技巧建议（如果指定）
            technique_suggestion = ""
            if technique_id and self.memory_engine:
                technique_suggestion = await self.memory_engine.apply_technique(
                    technique_id,
                    {"scene_type": scene_type, "emotion": emotion}
                )
            
            # 构建场景 Prompt
            prompt = self._build_scene_prompt(
                scene_type=scene_type,
                description=scene_description,
                characters=characters,
                emotion=emotion,
                technique_suggestion=technique_suggestion
            )
            
            # 生成场景
            content = await self.call_llm(prompt, temperature=0.7)
            
            return {
                "status": "success",
                "scene_type": scene_type,
                "content": content,
                "word_count": len(content),
                "technique_applied": technique_id is not None
            }
        
        except Exception as e:
            logger.error(f"场景撰写失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "场景撰写失败"
            }
        
        finally:
            self.state = "idle"
    
    async def continue_chapter(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        续写章节（从中断处继续）
        
        输入:
        {
            "chapter_num": 5,
            "existing_content": "已有内容",
            "continue_outline": "后续大纲",
            "word_count_target": 1000
        }
        
        输出:
        {
            "status": "success",
            "continued_content": "续写内容",
            "word_count": 1200
        }
        """
        chapter_num = task.get('chapter_num')
        existing_content = task.get('existing_content', '')
        continue_outline = task.get('continue_outline', '')
        word_count_target = task.get('word_count_target', 1000)
        
        logger.info(f"续写第{chapter_num}章")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请续写以下章节内容。

## 已有内容（最后部分）
{existing_content[-2000:]}

## 后续大纲
{continue_outline}

## 续写要求
- 保持风格一致
- 承接上文情节
- 字数：{word_count_target}字左右
- 自然过渡，不要重复已有内容

请从已有内容的结尾处自然 continuation，直接输出续写内容。"""
            
            content = await self.call_llm(prompt, temperature=0.7)
            
            return {
                "status": "success",
                "continued_content": content,
                "word_count": len(content)
            }
        
        except Exception as e:
            logger.error(f"章节续写失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "章节续写失败"
            }
        
        finally:
            self.state = "idle"
    
    async def revise_chapter(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        修改章节（根据反馈）
        
        输入:
        {
            "chapter_num": 5,
            "original_content": "原内容",
            "feedback": {...},
            "revision_focus": ["dialogue", "pacing", ...]
        }
        
        输出:
        {
            "status": "success",
            "revised_content": "修改后内容",
            "revisions_made": [...]
        }
        """
        chapter_num = task.get('chapter_num')
        original_content = task.get('original_content', '')
        feedback = task.get('feedback', {})
        revision_focus = task.get('revision_focus', [])
        
        logger.info(f"修改第{chapter_num}章")
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            prompt = f"""请根据以下反馈修改章节内容。

## 原章节内容
{original_content[:8000]}

## 修改反馈
- 优点：{feedback.get('strengths', [])}
- 问题：{feedback.get('weaknesses', [])}
- 建议：{feedback.get('suggestions', [])}

## 修改重点
{revision_focus}

## 修改要求
1. 保留优点
2. 修复指出的问题
3. 采纳合理的建议
4. 保持风格一致

请输出修改后的完整章节内容。"""
            
            content = await self.call_llm(prompt, temperature=0.5)  # 较低温度保持稳定
            
            return {
                "status": "success",
                "revised_content": content,
                "revisions_made": revision_focus
            }
        
        except Exception as e:
            logger.error(f"章节修改失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "章节修改失败"
            }
        
        finally:
            self.state = "idle"
    
    # ========== 辅助方法 ==========
    
    def _build_chapter_prompt(
        self,
        chapter_num: int,
        title: str,
        outline: str,
        word_count: int,
        style_context: Dict,
        memory_context: Dict
    ) -> str:
        """构建章节写作 Prompt"""
        
        parts = []
        
        # 角色定义
        parts.append("""你正在撰写小说章节。请遵循以下指导：""")
        
        # 章节信息
        parts.append(f"""
## 章节信息
- 章节号：第{chapter_num}章
- 标题：{title}
- 目标字数：{word_count}字左右
""")
        
        # 大纲
        if outline:
            parts.append(f"""
## 本章大纲
{outline}
""")
        
        # 风格指导
        if style_context:
            parts.append(f"""
## 当前写作风格：{style_context.get('style_name', '默认风格')}
{style_context.get('description', '')}

**风格维度**:
- 叙事节奏：{'快' if style_context.get('narrative_pace', 5) > 5 else '慢' if style_context.get('narrative_pace', 5) < 5 else '中等'}
- 描写密度：{'详尽' if style_context.get('description_density', 5) > 5 else '简洁' if style_context.get('description_density', 5) < 5 else '中等'}
- 对话比例：{'多' if style_context.get('dialogue_ratio', 5) > 5 else '少' if style_context.get('dialogue_ratio', 5) < 5 else '中等'}
- 情感强度：{'激烈' if style_context.get('emotional_intensity', 5) > 5 else '含蓄' if style_context.get('emotional_intensity', 5) < 5 else '中等'}

**写作指导原则**:
{chr(10).join(f"- {g}" for g in style_context.get('guidelines', [])[:5])}

**语气示例**:
{style_context.get('tone_examples', [''])[0][:200] if style_context.get('tone_examples') else ''}
""")
        
        # 记忆上下文
        if memory_context:
            # 前情提要
            if memory_context.get('previous_chapter_summary'):
                parts.append(f"""
## 前情提要
{memory_context.get('previous_chapter_summary')}
""")
            
            # 人物状态
            if memory_context.get('character_states'):
                parts.append(f"""
## 当前人物状态
{memory_context.get('character_states')}
""")
            
            # 可用技巧
            techniques = memory_context.get('techniques', [])
            if techniques:
                parts.append(f"""
## 推荐应用的写作技巧
{chr(10).join(f"- {t.get('name', '技巧')}: {t.get('description', '')[:100]}" for t in techniques[:3])}
""")
        
        # 写作要求
        parts.append(f"""
## 写作要求
- 字数：{word_count}字左右
- 保持风格统一
- 情节连贯，人物不 OOC
- 开篇吸引人，结尾有悬念
- 对话自然，描写有画面感

请开始撰写本章内容。直接输出章节正文，不需要额外说明。""")
        
        return "\n".join(parts)
    
    def _build_scene_prompt(
        self,
        scene_type: str,
        description: str,
        characters: List[str],
        emotion: str,
        technique_suggestion: str = ""
    ) -> str:
        """构建场景写作 Prompt"""
        
        scene_type_names = {
            'opening': '开篇场景',
            'climax': '高潮场景',
            'transition': '过渡场景',
            'ending': '结尾场景',
            'normal': '普通场景'
        }
        
        emotion_names = {
            'tense': '紧张',
            'romantic': '浪漫',
            'sad': '悲伤',
            'exciting': '激动',
            'neutral': '平静'
        }
        
        return f"""请撰写以下场景。

## 场景类型
{scene_type_names.get(scene_type, '场景')}

## 场景描述
{description}

## 出场人物
{', '.join(characters) if characters else '无特定人物'}

## 情感基调
{emotion_names.get(emotion, '中性')}

{f"""## 技巧应用建议
{technique_suggestion}""" if technique_suggestion else ""}

## 写作要求
- 创造沉浸式体验
- 调动五感描写
- 对话自然流畅
- 符合场景类型特点

请输出场景内容。"""
    
    def _detect_scene_type(self, outline: str) -> str:
        """检测场景类型"""
        outline_lower = outline.lower()
        
        if any(kw in outline_lower for kw in ['开始', '引入', '初次', '第一']):
            return 'opening'
        elif any(kw in outline_lower for kw in ['高潮', '决战', '爆发', '最终']):
            return 'climax'
        elif any(kw in outline_lower for kw in ['过渡', '转折', '之后', '随后']):
            return 'transition'
        elif any(kw in outline_lower for kw in ['结束', '收尾', '结局', '最后']):
            return 'ending'
        else:
            return 'normal'
    
    def _detect_emotion(self, outline: str) -> str:
        """检测情感基调"""
        outline_lower = outline.lower()
        
        if any(kw in outline_lower for kw in ['紧张', '危险', '危机', '战斗']):
            return 'tense'
        elif any(kw in outline_lower for kw in ['浪漫', '爱情', '心动', '温柔']):
            return 'romantic'
        elif any(kw in outline_lower for kw in ['悲伤', '失落', '痛苦', '死亡']):
            return 'sad'
        elif any(kw in outline_lower for kw in ['兴奋', '激动', '胜利', '惊喜']):
            return 'exciting'
        else:
            return 'neutral'
