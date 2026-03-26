# ==========================================
# 多 Agent 协作小说系统 - 小说架构师 Agent
# 负责全自动创作的核心 Agent
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
import httpx

logger = logging.getLogger(__name__)


class NovelArchitectAgent:
    """
    小说架构师 Agent
    负责全自动创作的核心规划和协调
    """
    
    def __init__(self, llm_client: Dict[str, Any]):
        self.llm_client = llm_client
        self.agent_id = "novel_architect"
        self.state = "idle"
        self.last_active = None
    
    async def create_novel_blueprint(
        self,
        title: str,
        genre: str,
        description: str,
        chapter_count: int = 3000
    ) -> Dict[str, Any]:
        """
        创建小说蓝图（全自动）
        
        流程:
        1. 生成世界观地图
        2. 生成 3000 章宏观规划
        3. 生成人物体系
        4. 生成伏笔网络
        5. 整合所有设定
        """
        
        self.state = "working"
        self.last_active = datetime.now()
        
        try:
            # Step 1: 生成世界观地图
            logger.info(f"Step 1: 生成世界观地图 - {title}")
            world_map = await self._generate_world_map(title, genre, description, chapter_count)
            
            # Step 2: 生成宏观规划
            logger.info(f"Step 2: 生成 3000 章宏观规划")
            macro_plot = await self._generate_macro_plot(title, genre, world_map, chapter_count)
            
            # Step 3: 生成人物体系
            logger.info(f"Step 3: 生成人物体系")
            character_system = await self._generate_character_system(title, genre, world_map, macro_plot)
            
            # Step 4: 生成伏笔网络
            logger.info(f"Step 4: 生成伏笔网络")
            hook_network = await self._generate_hook_network(title, world_map, macro_plot)
            
            # Step 5: 整合蓝图
            blueprint = {
                "novel_info": {
                    "title": title,
                    "genre": genre,
                    "description": description,
                    "chapter_count": chapter_count,
                    "created_at": datetime.now().isoformat()
                },
                "world_map": world_map,
                "macro_plot": macro_plot,
                "character_system": character_system,
                "hook_network": hook_network,
                "status": "completed",
                "completion_time": datetime.now().isoformat()
            }
            
            self.state = "idle"
            return blueprint
            
        except Exception as e:
            logger.error(f"创建蓝图失败：{e}")
            self.state = "error"
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_world_map(self, title: str, genre: str, description: str, chapter_count: int) -> Dict[str, Any]:
        """生成世界观地图 - 简化版"""
        prompt = f"""你是一位专业的世界观架构师。为小说《{title}》生成世界观设定。

类型：{genre}
简介：{description}

请用 JSON 格式输出：
{{
  "world_name": "世界名称",
  "power_system": {{
    "name": "修炼体系",
    "levels": ["等级 1", "等级 2", "等级 3"]
  }},
  "main_factions": [
    {{"name": "势力 1", "description": "描述"}}
  ],
  "background": "世界背景（500 字内）"
}}

只需 JSON，不要其他说明。"""
        
        response = await self._call_llm(prompt, max_tokens=2000)
        
        try:
            world_map = self._extract_json(response)
            return world_map
        except Exception as e:
            logger.error(f"解析世界观失败：{e}")
            return {"raw": response[:500], "parse_error": str(e)}
    
    async def _generate_macro_plot(self, title: str, genre: str, world_map: Dict, chapter_count: int) -> Dict[str, Any]:
        """生成宏观规划 - 简化版"""
        prompt = f"""你是一位专业的长篇规划师。为小说《{title}》生成{chapter_count}章规划。

类型：{genre}
世界观：{json.dumps(world_map, ensure_ascii=False)[:500]}

请用 JSON 格式输出：
{{
  "total_chapters": {chapter_count},
  "volumes": [
    {{
      "volume_num": 1,
      "volume_title": "第一卷标题",
      "chapters": "1-20",
      "main_goal": "本卷目标",
      "conflict": "核心冲突",
      "climax_chapter": 20
    }}
  ],
  "rhythm_control": {{
    "small_climax": "每 5 章一个小高潮",
    "medium_climax": "每 10 章一个中高峰",
    "big_climax": "每 20 章一个大高潮"
  }}
}}

只需 JSON，不要其他说明。"""
        
        response = await self._call_llm(prompt, max_tokens=3000)
        
        try:
            macro_plot = self._extract_json(response)
            return macro_plot
        except Exception as e:
            logger.error(f"解析规划失败：{e}")
            return {"raw": response[:500], "parse_error": str(e)}
    
    async def _generate_character_system(self, title: str, genre: str, world_map: Dict, macro_plot: Dict) -> Dict[str, Any]:
        """生成人物体系 - 简化版"""
        prompt = f"""为小说《{title}》生成主角设定。

类型：{genre}

请用 JSON 格式输出：
{{
  "protagonist": {{
    "name": "主角名",
    "age": 18,
    "background": "背景故事（200 字）",
    "personality": ["性格 1", "性格 2"],
    "goal": "核心目标"
  }}
}}

只需 JSON，不要其他说明。"""
        
        response = await self._call_llm(prompt, max_tokens=1500)
        
        try:
            characters = self._extract_json(response)
            return characters
        except Exception as e:
            logger.error(f"解析人物失败：{e}")
            return {"protagonist": {"name": "待生成", "background": response[:200]}}
    
    async def _generate_hook_network(self, title: str, world_map: Dict, macro_plot: Dict) -> Dict[str, Any]:
        """生成伏笔网络 - 简化版"""
        return {
            "short_term": [{"description": "第一个小谜团", "reveal_chapter": 5}],
            "medium_term": [{"description": "中期大谜团", "reveal_chapter": 10}],
            "long_term": [{"description": "终极谜团", "reveal_chapter": 20}],
            "ultimate": [{"description": "全书核心谜团"}]
        }
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """从文本中提取 JSON"""
        try:
            # 查找 JSON 起始和结束位置
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("未找到 JSON 内容")
        except Exception as e:
            logger.error(f"提取 JSON 失败：{e}")
            # 返回原始文本
            return {"raw": text}
    
    async def _call_llm(self, prompt: str, max_tokens: int = 4000) -> str:
        """调用 LLM API"""
        if not self.llm_client:
            raise Exception("LLM 未配置")
        
        api_key = self.llm_client['api_key']
        base_url = self.llm_client['base_url']
        model = self.llm_client['model']
        timeout = self.llm_client['timeout']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的小说架构师，擅长构建宏大而自洽的世界观和长篇规划。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                raise Exception(f"LLM API 调用失败：{response.status_code} - {response.text}")


# ========== 全自动创作系统 ==========

class AutoCreationSystem:
    """
    全自动创作系统
    一键生成完整小说设定和章节
    """
    
    def __init__(self, llm_client: Dict[str, Any]):
        self.llm_client = llm_client
        self.architect = NovelArchitectAgent(llm_client)
        self.blueprint: Optional[Dict[str, Any]] = None
    
    async def create_novel_from_scratch(
        self,
        title: str,
        genre: str,
        description: str,
        chapter_count: int = 3000
    ) -> Dict[str, Any]:
        """
        从零开始创建小说（全自动）
        
        用户只需要提供:
        - 书名
        - 类型
        - 一句话简介
        
        系统自动生成:
        - 世界观地图
        - 3000 章规划
        - 人物体系
        - 伏笔网络
        - 第一章正文
        """
        
        logger.info(f"开始全自动创作：{title}")
        
        # Step 1: 创建蓝图
        self.blueprint = await self.architect.create_novel_blueprint(
            title, genre, description, chapter_count
        )
        
        if self.blueprint.get('status') == 'error':
            return self.blueprint
        
        # Step 2: 保存蓝图到数据库
        from app.novel_db import get_novel_database
        db = get_novel_database()
        
        # 创建小说
        novel_id = db.create_novel(title, genre, description)
        
        # 保存世界观
        # 保存宏观规划
        # 保存人物体系
        # 保存伏笔网络
        
        # Step 3: 生成第一章
        first_chapter = await self._generate_first_chapter(novel_id, self.blueprint)
        
        return {
            "status": "success",
            "novel_id": novel_id,
            "blueprint": self.blueprint,
            "first_chapter": first_chapter
        }
    
    async def _generate_first_chapter(self, novel_id: str, blueprint: Dict) -> Dict[str, Any]:
        """生成第一章 - 修复版：严格验证内容有效性"""
        from app.workflow_executor import get_workflow_executor
        from app.novel_db import get_novel_database
        import json
        
        executor = get_workflow_executor()
        db = get_novel_database()
        
        # 从蓝图中提取第一章大纲
        chapter_outline = self._extract_first_chapter_outline(blueprint)
        
        logger.info(f"开始生成第一章，大纲：{chapter_outline[:100]}...")
        
        # 先创建章节记录
        try:
            db.create_chapter(novel_id, 1, "第一章 开始", chapter_outline)
            logger.info(f"[OK] 已创建章节记录：{novel_id} 第 1 章")
        except Exception as e:
            logger.error(f"[FAIL] 创建章节记录失败：{e}，继续生成内容")
        
        # 生成第一章内容
        logger.info(f"调用 workflow_executor 生成第一章内容...")
        result = await executor.execute_chapter_workflow(
            novel_id=novel_id,
            chapter_num=1,
            outline=chapter_outline,
            word_count_target=3000
        )
        
        logger.info(f"workflow_executor 返回：status={result.get('status')}, word_count={result.get('word_count', 0)}")
        
        # 修复：严格检查内容是否有效
        content = result.get('content', '')
        if result.get('status') == 'success' and content and len(content) > 100:
            logger.info(f"[OK] 第一章生成成功，字数：{len(content)}")
            try:
                db.update_chapter(
                    novel_id, 1,
                    content=content,
                    title="第一章",
                    outline=chapter_outline,
                    status='published'
                )
                logger.info(f"[OK] 已保存第一章内容到数据库：{novel_id}")
            except Exception as e:
                logger.error(f"[FAIL] 保存章节内容失败：{e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            # 内容无效，记录详细错误
            logger.error(f"[FAIL] 第一章生成失败或内容为空")
            logger.error(f"   status: {result.get('status')}")
            logger.error(f"   content length: {len(content) if content else 0}")
            logger.error(f"   message: {result.get('message', 'N/A')}")
            logger.error(f"   full result: {json.dumps(result, ensure_ascii=False)[:500]}")
        
        return result
    
    def _extract_first_chapter_outline(self, blueprint: Dict) -> str:
        """从蓝图中提取第一章大纲"""
        # 简化实现
        return "主角登场，引入世界观，第一个小冲突"


# ========== 全局单例 ==========

_creation_system: Optional[AutoCreationSystem] = None


def get_auto_creation_system() -> AutoCreationSystem:
    """获取全自动创作系统单例"""
    global _creation_system
    if _creation_system is None:
        from app.config_db import get_config_database
        db = get_config_database()
        
        default_provider = db.get_default_provider()
        provider_config = db.get_provider(default_provider)
        
        if provider_config and provider_config.get('api_key'):
            llm_client = {
                'api_key': provider_config['api_key'],
                'base_url': provider_config['base_url'],
                'model': provider_config['model'],
                'timeout': provider_config.get('timeout', 60)
            }
            _creation_system = AutoCreationSystem(llm_client)
        else:
            raise Exception("LLM 未配置")
    
    return _creation_system
