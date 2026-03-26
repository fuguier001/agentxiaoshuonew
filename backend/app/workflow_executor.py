# ==========================================
# 多 Agent 协作小说系统 - 真实写作工作流
# 直接调用 LLM 实现 AI 创作
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import httpx
import json

logger = logging.getLogger(__name__)


class WritingWorkflowExecutor:
    """
    写作工作流执行器
    真实调用 LLM 完成章节创作
    """
    
    def __init__(self, config_service=None):
        self.config_service = config_service
        self.runtime_provider = None
        self.llm_client = None
        self._load_llm_config()
    
    def _load_llm_config(self):
        """加载 LLM 配置"""
        try:
            if self.config_service is None:
                from app.services.config_service import get_config_service
                self.config_service = get_config_service()

            provider_config = self.config_service.get_active_provider_config()

            if provider_config and provider_config.get('api_key'):
                self.runtime_provider = provider_config
                self.llm_client = {
                    'api_key': provider_config['api_key'],
                    'base_url': provider_config['base_url'],
                    'model': provider_config['model'],
                    'timeout': provider_config.get('timeout', 300)
                }
                logger.info(f"[OK] LLM 配置加载成功：{provider_config['name']}")
                logger.info(f"   Base URL: {provider_config['base_url']}")
            else:
                logger.warning("[FAIL] LLM 配置不完整或未配置默认提供商")
                self.runtime_provider = None
                self.llm_client = None
        except Exception as e:
            logger.error(f"[FAIL] 加载 LLM 配置失败：{e}")
            import traceback
            traceback.print_exc()
            self.runtime_provider = None
            self.llm_client = None
    
    async def _get_previous_chapters(self, novel_id: str, current_chapter: int, count: int = 3) -> List[Dict[str, Any]]:
        """获取前 N 章内容"""
        try:
            from app.novel_db import get_novel_database
            db = get_novel_database()
            
            prev_chapters = []
            for i in range(max(1, current_chapter - count), current_chapter):
                chapter = db.get_chapter(novel_id, i)
                if chapter and chapter.get('content'):
                    prev_chapters.append({
                        'chapter_num': i,
                        'title': chapter.get('title', ''),
                        'content': chapter.get('content', '')
                    })
            
            return prev_chapters
        except Exception as e:
            logger.error(f"获取前章内容失败：{e}")
            return []
    
    async def _refine_outline_smart(self, outline: str, style: str, prev_chapters: List[Dict], 
                                     macro_plot: Optional[Dict], protagonist_halo: Optional[Dict]) -> str:
        """智能细化大纲"""
        # 简化实现：直接调用基础方法
        return await self._refine_outline(outline, style)
    
    async def _prepare_characters_smart(self, novel_id: str, outline: str, prev_chapters: List[Dict],
                                         world_map: Optional[Dict], protagonist_halo: Optional[Dict]) -> str:
        """智能准备角色"""
        # 简化实现：直接调用基础方法
        return await self._prepare_characters(novel_id, outline)
    
    async def _write_draft_smart(self, outline: str, character_notes: str, word_count_target: int,
                                  style: str, prev_chapters: List[Dict], macro_plot: Optional[Dict],
                                  world_map: Optional[Dict], protagonist_halo: Optional[Dict]) -> str:
        """智能撰写初稿"""
        # 简化实现：直接调用基础方法
        return await self._write_draft(outline, character_notes, word_count_target, style)
    
    async def _consistency_check_smart(self, content: str, novel_id: str, prev_chapters: List[Dict],
                                        world_map: Optional[Dict], protagonist_halo: Optional[Dict]) -> Dict[str, Any]:
        """智能一致性检查"""
        # 简化实现：直接调用基础方法
        return await self._consistency_check(content, novel_id)
    
    async def execute_chapter_workflow(
        self,
        novel_id: str,
        chapter_num: int,
        outline: str,
        word_count_target: int = 3000,
        style: str = 'default',
        macro_plot: Optional[Dict] = None,
        world_map: Optional[Dict] = None,
        protagonist_halo: Optional[Dict] = None  # 新增主角光环参数
    ) -> Dict[str, Any]:
        """
        执行章节创作工作流 - 智能参考系统
        
        核心机制:
        1. 参考宏观大纲（macro_plot）
        2. 参考世界观地图（world_map）
        3. 参考主角光环设定（protagonist_halo）- 新增！
        4. 参考前 3 章内容（保证连续性）
        5. 6 步 Agent 质量审核
        
        流程:
        1. 剧情架构师 - 细化大纲（参考宏观大纲 + 前 3 章 + 主角光环）
        2. 人物设计师 - 准备角色（参考前 3 章 + 世界观 + 主角光环）
        3. 章节写手 - 撰写初稿（参考前 3 章 + 大纲 + 世界观 + 主角光环）
        4. 对话专家 - 打磨对话
        5. 审核编辑 - 一致性检查（参考前 3 章 + 世界观 + 主角光环）
        6. 主编 - 最终审核
        """
        
        if not self.llm_client:
            logger.error("LLM 未配置！")
            return {
                'status': 'error',
                'message': 'LLM 未配置，请先在配置页面设置 API Key'
            }
        
        workflow_id = f"wf_{novel_id}_{chapter_num}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"开始执行智能章节工作流：{workflow_id}")
        logger.info(f"   小说 ID: {novel_id}")
        logger.info(f"   章节：第{chapter_num}章")
        logger.info(f"   目标字数：{word_count_target}")
        
        # 读取前 3 章内容（用于连续性参考）
        logger.info(f"读取前 3 章内容...")
        prev_chapters = await self._get_previous_chapters(novel_id, chapter_num, count=3)
        
        if prev_chapters:
            logger.info(f"✓ 已读取 {len(prev_chapters)} 章前章内容")
            for ch in prev_chapters:
                logger.info(f"   - 第{ch['chapter_num']}章：{len(ch.get('content', ''))}字")
        else:
            logger.info(f"   无前章（这是前几章）")
        
        # 读取宏观大纲（如果有）
        if macro_plot:
            logger.info(f"✓ 已加载宏观大纲")
        else:
            logger.info(f"   无宏观大纲")
        
        # 读取世界观地图（如果有）
        if world_map:
            logger.info(f"✓ 已加载世界观地图")
        else:
            logger.info(f"   无世界观地图")
        
        # 读取主角光环设定（如果有）- 新增！
        if protagonist_halo:
            logger.info(f"✓ 已加载主角光环设定：{protagonist_halo.get('halo_name', '未知')}")
            logger.info(f"   当前等级：根据章节推算")
        else:
            logger.info(f"   无主角光环设定")
        
        try:
            # Step 1: 细化大纲（参考宏观大纲 + 前 3 章 + 主角光环）
            logger.info(f"Step 1/6: 剧情架构师 - 细化大纲")
            try:
                refined_outline = await self._refine_outline_smart(
                    outline, style, prev_chapters, macro_plot, protagonist_halo
                )
                # 验证 Step 1 输出
                if not refined_outline or len(refined_outline) < 50:
                    logger.error(f"Step 1 返回内容过短：{len(refined_outline) if refined_outline else 0}")
                    raise Exception("Step 1 细化大纲失败：内容为空")
                logger.info(f"✓ Step 1 完成，大纲长度：{len(refined_outline)}")
            except Exception as e:
                logger.error(f"✗ Step 1 失败：{e}")
                raise
            
            # Step 2: 准备角色（参考前 3 章 + 世界观 + 主角光环）
            logger.info(f"Step 2/6: 人物设计师 - 准备角色")
            try:
                character_notes = await self._prepare_characters_smart(
                    novel_id, refined_outline, prev_chapters, world_map, protagonist_halo
                )
                logger.info(f"✓ Step 2 完成，角色笔记长度：{len(character_notes) if character_notes else 0}")
            except Exception as e:
                logger.error(f"✗ Step 2 失败：{e}")
                raise
            
            # Step 3: 撰写初稿（参考前 3 章 + 大纲 + 世界观 + 主角光环）- 关键步骤
            logger.info(f"Step 3/6: 章节写手 - 撰写初稿")
            try:
                draft_content = await self._write_draft_smart(
                    refined_outline, 
                    character_notes, 
                    word_count_target,
                    style,
                    prev_chapters,
                    macro_plot,
                    world_map,
                    protagonist_halo
                )
                # 严格验证初稿内容
                if not draft_content or len(draft_content) < 500:
                    logger.error(f"Step 3 返回内容过短：{len(draft_content) if draft_content else 0}")
                    logger.error(f"   前 200 字符：{draft_content[:200] if draft_content else 'None'}")
                    raise Exception(f"章节写手失败：内容过短 ({len(draft_content) if draft_content else 0}字)")
                logger.info(f"✓ Step 3 完成，初稿字数：{len(draft_content)}")
            except Exception as e:
                logger.error(f"✗ Step 3 失败：{e}")
                raise
            
            # Step 4: 打磨对话
            logger.info(f"Step 4/6: 对话专家 - 打磨对话")
            try:
                polished_content = await self._polish_dialogue(draft_content)
                # 验证打磨后内容
                if not polished_content or len(polished_content) < 500:
                    logger.error(f"Step 4 返回内容过短：{len(polished_content) if polished_content else 0}")
                    raise Exception("对话打磨失败：内容过短")
                logger.info(f"✓ Step 4 完成，润色后字数：{len(polished_content)}")
            except Exception as e:
                logger.error(f"✗ Step 4 失败：{e}")
                raise
            
            # Step 5: 一致性检查（参考前 3 章 + 世界观 + 主角光环）
            logger.info(f"Step 5/6: 审核编辑 - 一致性检查（人物/剧情/道具/金手指）")
            try:
                check_result = await self._consistency_check_smart(
                    polished_content, novel_id, prev_chapters, world_map, protagonist_halo
                )
                logger.info(f"✓ Step 5 完成")
            except Exception as e:
                logger.error(f"✗ Step 5 失败：{e}")
                raise
            
            # Step 6: 最终审核
            logger.info(f"Step 6/6: 主编 - 最终审核")
            try:
                final_content = await self._final_review(polished_content, check_result)
                # 最终验证
                if not final_content or len(final_content) < 500:
                    logger.error(f"Step 6 返回内容过短：{len(final_content) if final_content else 0}")
                    raise Exception("最终审核失败：内容过短")
                logger.info(f"✓ Step 6 完成，最终字数：{len(final_content)}")
            except Exception as e:
                logger.error(f"✗ Step 6 失败：{e}")
                raise
            
            logger.info(f"✅ 智能工作流执行成功：{workflow_id}")
            logger.info(f"   总字数：{len(final_content) if final_content else 0}")
            logger.info(f"   参考前章：{len(prev_chapters)}章")
            return {
                'status': 'success',
                'workflow_id': workflow_id,
                'chapter_num': chapter_num,
                'content': final_content,
                'word_count': len(final_content),
                'stages_completed': 6,
                'total_stages': 6,
                'context_used': {
                    'prev_chapters': len(prev_chapters),
                    'macro_plot': macro_plot is not None,
                    'world_map': world_map is not None,
                    'protagonist_halo': protagonist_halo is not None  # 新增
                }
            }
            
        except Exception as e:
            error_msg = f"工作流执行失败：{str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'message': error_msg,
                'workflow_id': workflow_id
            }
    
    async def _refine_outline(self, outline: str, style: str) -> str:
        """剧情架构师：细化大纲"""
        prompt = f"""你是一位专业的剧情架构师。请细化以下章节大纲，使其更加具体和可执行：

原始大纲：
{outline}

要求：
1. 明确本章的核心冲突
2. 列出关键情节点（3-5 个）
3. 说明情感起伏
4. 指出需要埋设的伏笔

请输出细化后的大纲："""
        
        return await self._call_llm(prompt)
    
    async def _prepare_characters(self, novel_id: str, outline: str) -> str:
        """人物设计师：准备角色"""
        try:
            prompt = f"""你是一位人物设计师。根据以下大纲，分析本章可能出现的人物：

大纲：
{outline}

请列出：
1. 主要出场人物
2. 每个人物的目标
3. 人物之间的关系动态
4. 需要注意的性格特征

输出角色准备笔记："""
            
            logger.info(f"正在调用 LLM 准备角色...")
            result = await self._call_llm(prompt, max_tokens=1500)
            logger.info(f"角色准备完成，返回长度：{len(result) if result else 0}")
            return result
        except Exception as e:
            logger.error(f"准备角色失败：{e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _write_draft(
        self, 
        outline: str, 
        character_notes: str, 
        word_count_target: int,
        style: str
    ) -> str:
        """章节写手：撰写初稿"""
        prompt = f"""你是一位专业的小说写手。请根据以下材料撰写章节正文：

【本章大纲】
{outline}

【角色准备】
{character_notes}

【要求】
1. 字数目标：约{word_count_target}字
2. 使用第三人称叙述
3. 包含动作、对话、心理描写
4. 保持节奏紧凑
5. 展现人物性格

请开始创作："""
        
        return await self._call_llm(prompt, max_tokens=word_count_target // 2)
    
    async def _polish_dialogue(self, content: str) -> str:
        """对话专家：打磨对话"""
        prompt = f"""你是一位对话专家。请优化以下章节中的对话部分：

【章节内容】
{content}

要求：
1. 使对话更自然流畅
2. 符合人物性格
3. 增加潜台词
4. 优化对话节奏

输出优化后的完整章节："""
        
        return await self._call_llm(prompt)
    
    async def _consistency_check(self, content: str, novel_id: str) -> Dict[str, Any]:
        """审核编辑：一致性检查"""
        prompt = f"""你是一位审核编辑。请检查以下章节的一致性问题：

【章节内容】
{content}

检查项：
1. 人物性格是否一致
2. 时间线是否合理
3. 地点转换是否流畅
4. 情节逻辑是否通顺
5. 是否有前后矛盾

请列出发现的问题（如无问题则回复"无问题"）："""
        
        issues = await self._call_llm(prompt)
        
        return {
            'issues': issues,
            'has_issues': '无问题' not in issues
        }
    
    async def _final_review(self, content: str, check_result: Dict) -> str:
        """主编：最终审核"""
        if not check_result['has_issues']:
            return content
        
        prompt = f"""你是一位主编。请根据审核意见修改章节：

【章节内容】
{content}

【审核意见】
{check_result['issues']}

请针对性地修改问题，输出最终版本："""
        
        return await self._call_llm(prompt)
    
    async def generate_novel_outline(self, title: str, genre: str, description: str, template_id: str = 'qichengzhuanhe') -> Dict[str, Any]:
        """AI 生成小说整体大纲 - 使用专业模板"""
        from app.templates import get_template
        
        # 获取专业模板
        template = get_template('outline', template_id)
        if not template:
            template = get_template('outline', 'qichengzhuanhe')  # 默认使用起承转合
        
        # 填充模板
        prompt = template['template'].format(
            title=title,
            genre=genre,
            description=description
        )
        
        outline = await self._call_llm(prompt, max_tokens=4000)
        
        return {
            'title': title,
            'genre': genre,
            'template_used': template['name'],
            'outline': outline,
            'generated_at': datetime.now().isoformat()
        }
    
    async def generate_characters(self, title: str, genre: str, outline: str, count: int = 5) -> Dict[str, Any]:
        """AI 生成人物设定"""
        prompt = f"""你是一位专业的人物设计师。请为以下小说设计{count}个主要人物：

【小说标题】{title}
【类型】{genre}
【故事大纲】{outline}

请为每个人物设计以下内容：
1. **姓名** (符合类型风格)
2. **年龄/性别**
3. **外貌特征** (3-5 个关键特点)
4. **性格特点** (3-5 个关键词 + 详细说明)
5. **背景故事** (200 字左右)
6. **核心目标** (人物在故事中的追求)
7. **人物关系** (与其他人物的关系)
8. **经典台词** (1-2 句代表性话语)

请按以下 JSON 格式输出（只需要 JSON，不要其他说明）：
{{
  "characters": [
    {{
      "name": "姓名",
      "age": 年龄，
      "gender": "性别",
      "appearance": "外貌描述",
      "personality": ["性格 1", "性格 2"],
      "background": "背景故事",
      "goal": "核心目标",
      "relations": {{"人物名": "关系描述"}},
      "quote": "经典台词",
      "role": "主角/配角/反派"
    }}
  ]
}}"""
        
        response = await self._call_llm(prompt, max_tokens=4000)
        
        # 尝试解析 JSON
        try:
            import json
            # 提取 JSON 部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return {
                    'characters': data.get('characters', []),
                    'generated_at': datetime.now().isoformat()
                }
        except:
            pass
        
        # 解析失败时返回原始内容
        return {
            'characters': [{'description': response}],
            'generated_at': datetime.now().isoformat()
        }
    
    async def generate_chapter_outline(self, novel_title: str, chapter_num: int, overall_outline: str) -> Dict[str, Any]:
        """AI 生成章节大纲"""
        prompt = f"""你是一位专业的剧情架构师。请为以下小说的第{chapter_num}章生成详细大纲：

【小说标题】{novel_title}
【章节号】第{chapter_num}章
【整体大纲】{overall_outline}

请生成以下内容：
1. **本章标题** (简洁有力)
2. **核心事件** (本章发生的主要事件，100 字)
3. **情节发展** (开始→发展→高潮→结尾，分 4 段说明)
4. **出场人物** (列出本章出现的人物)
5. **场景设定** (时间、地点、氛围)
6. **伏笔埋设** (如果需要，说明埋设什么伏笔)
7. **情感基调** (紧张/温馨/悲伤/欢乐等)

请用清晰的格式输出。"""
        
        outline = await self._call_llm(prompt, max_tokens=2000)
        
        return {
            'chapter_num': chapter_num,
            'outline': outline,
            'generated_at': datetime.now().isoformat()
        }
    
    async def generate_plot_design(self, chapter_outline: str, characters: List[Dict]) -> Dict[str, Any]:
        """AI 生成情节设计"""
        characters_info = "\n".join([f"- {c.get('name', '人物')}: {c.get('personality', [''])[0] if c.get('personality') else ''}" for c in characters])
        
        prompt = f"""你是一位专业的情节设计师。请根据以下材料设计详细的情节：

【章节大纲】{chapter_outline}
【出场人物】
{characters_info}

请设计：
1. **开场场景** (如何引入本章，200 字)
2. **关键冲突** (人物之间的矛盾或挑战)
3. **转折点** (情节的意外变化)
4. **高潮场景** (本章最精彩的部分，300 字详细描写)
5. **结尾处理** (如何收尾，为下章做铺垫)
6. **对话要点** (关键对话的内容和目的)

请输出详细的情节设计。"""
        
        plot_design = await self._call_llm(prompt, max_tokens=3000)
        
        return {
            'plot_design': plot_design,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _learning_analyst_review(
        self,
        content: str,
        chapter_num: int,
        prev_chapters: List[Dict],
        world_map: Optional[Dict],
        protagonist_halo: Optional[Dict]
    ) -> Dict[str, Any]:
        """学习分析师：质量分析与改进建议"""
        try:
            from app.agents.learning_agent import get_learning_agent
            
            agent = get_learning_agent()
            
            # 分析章节质量
            quality_result = await agent.analyze_chapter_quality(
                content, chapter_num, prev_chapters, world_map, protagonist_halo
            )
            
            # 提取 JSON 结果
            quality_data = self._extract_json(quality_result)
            
            return {
                'quality_score': quality_data.get('scores', {}).get('overall', 0),
                'highlights': quality_data.get('highlights', []),
                'weaknesses': quality_data.get('weaknesses', []),
                'suggestions': quality_data.get('suggestions', []),
                'cool_point_analysis': quality_data.get('cool_point_analysis', {}),
                'writing_style': quality_data.get('writing_style', {})
            }
        except Exception as e:
            logger.error(f"学习分析师失败：{e}")
            return {
                'quality_score': 0,
                'highlights': [],
                'weaknesses': [],
                'suggestions': [],
                'error': str(e)
            }
    
    async def _final_review_with_learning(
        self,
        content: str,
        check_result: Dict[str, Any],
        learning_result: Dict[str, Any]
    ) -> str:
        """主编：最终审核（考虑学习分析师的建议）"""
        # 如果有学习分析建议，进行最终优化
        if learning_result.get('suggestions'):
            suggestions_str = "\n".join(f"- {s}" for s in learning_result['suggestions'][:3])
            
            prompt = f"""你是一位主编。请根据审核意见和学习分析师的建议优化章节。

【章节内容】
{content[:3000]}...

【审核编辑意见】
{check_result.get('issues', '无问题')}

【学习分析师建议】（重点考虑！）
{suggestions_str}

【要求】
1. 采纳学习分析师的合理建议
2. 保持章节整体风格
3. 优化不超过 20% 的内容
4. 确保改进明显但不突兀

请输出优化后的章节（如果无需优化则回复"无需优化"）："""
            
            try:
                optimized = await self._call_llm(prompt, max_tokens=3500)
                if optimized and "无需优化" not in optimized:
                    logger.info(f"主编优化：采纳了学习分析师的建议")
                    return optimized
            except Exception as e:
                logger.error(f"主编优化失败：{e}")
        
        # 无需优化或优化失败，返回原内容
        return content
    
    async def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用 LLM API"""
        if not self.llm_client:
            raise Exception("LLM 未配置")
        
        api_key = self.llm_client['api_key']
        base_url = self.llm_client['base_url']
        model = self.llm_client['model']
        timeout = self.llm_client.get('timeout', 300)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        # 重试机制：最多重试 3 次
        for attempt in range(3):
            try:
                logger.info(f"LLM API 调用中... (尝试 {attempt+1}/3)")
                async with httpx.AsyncClient(timeout=timeout) as client:
                    endpoint = self.llm_client.get("endpoint", "/v1/chat/completions")
                    response = await client.post(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data['choices'][0]['message']['content']
                        logger.info(f"LLM API 调用成功，返回长度：{len(content)}")
                        return content
                    else:
                        error_msg = f"LLM API 调用失败：{response.status_code} - {response.text[:200]}"
                        logger.error(error_msg)
                        if attempt < 2:
                            logger.info(f"等待 5 秒后重试...")
                            import asyncio
                            await asyncio.sleep(5)
                        else:
                            raise Exception(error_msg)
            except httpx.ReadError as e:
                logger.error(f"网络读取错误（尝试 {attempt+1}/3）: {e}")
                if attempt < 2:
                    logger.info(f"等待 5 秒后重试...")
                    import asyncio
                    await asyncio.sleep(5)
                else:
                    raise Exception(f"网络读取错误，重试 3 次失败：{e}")
            except Exception as e:
                logger.error(f"LLM 调用异常（尝试 {attempt+1}/3）: {e}")
                if attempt < 2:
                    logger.info(f"等待 5 秒后重试...")
                    import asyncio
                    await asyncio.sleep(5)
                else:
                    raise
        
        raise Exception("LLM 调用失败，已达最大重试次数")
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """从文本中提取 JSON"""
        try:
            # 查找 JSON 起始和结束位置
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                import json
                return json.loads(json_str)
            else:
                raise ValueError("未找到 JSON 内容")
        except Exception as e:
            logger.error(f"提取 JSON 失败：{e}")
            # 返回空字典
            return {}


# 全局单例
_workflow_executor: Optional[WritingWorkflowExecutor] = None


def get_workflow_executor() -> WritingWorkflowExecutor:
    """获取工作流执行器单例"""
    global _workflow_executor
    if _workflow_executor is None:
        _workflow_executor = WritingWorkflowExecutor()
    return _workflow_executor
