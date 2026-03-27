# ==========================================
# 多 Agent 协作小说系统 - 小说架构师 Agent
# 负责全自动创作的核心 Agent
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
import httpx
import asyncio
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# 断点续传状态文件目录
CHECKPOINT_DIR = Path("./data/checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


class NovelArchitectAgent:
    """
    小说架构师 Agent
    负责全自动创作的核心规划和协调
    支持断点续传
    """

    def __init__(self, llm_client: Dict[str, Any]):
        self.llm_client = llm_client
        self.agent_id = "novel_architect"
        self.state = "idle"
        self.last_active = None
        self.checkpoint_data: Dict[str, Any] = {}

    def _get_checkpoint_path(self, title: str) -> Path:
        """获取断点续传文件路径"""
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
        return CHECKPOINT_DIR / f"{safe_title}_checkpoint.json"

    def _save_checkpoint(self, title: str, step: int, data: Dict[str, Any]):
        """保存断点"""
        checkpoint = {
            "title": title,
            "step": step,
            "step_name": ["world_map", "macro_plot", "character_system", "hook_network", "completed"][step],
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        path = self._get_checkpoint_path(title)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        logger.info(f"断点已保存：Step {step} - {path}")

    def _load_checkpoint(self, title: str) -> Optional[Dict[str, Any]]:
        """加载断点"""
        path = self._get_checkpoint_path(title)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _clear_checkpoint(self, title: str):
        """清除断点"""
        path = self._get_checkpoint_path(title)
        if path.exists():
            os.remove(path)
            logger.info(f"断点已清除：{path}")

    def _update_progress(self, title: str, step: int, step_name: str, status: str, message: str = ""):
        """更新创作进度（供前端实时显示）"""
        from app.api.auto_routes import update_progress
        update_progress(title, step, step_name, status, message)

    async def create_novel_blueprint(
        self,
        title: str,
        genre: str,
        description: str,
        chapter_count: int = 3000,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        创建小说蓝图（全自动）- 支持断点续传

        流程:
        1. 生成世界观地图
        2. 生成 3000 章宏观规划
        3. 生成人物体系
        4. 生成伏笔网络
        5. 整合所有设定

        Args:
            resume: 是否从断点恢复
        """

        self.state = "working"
        self.last_active = datetime.now()

        # 初始化蓝图数据
        blueprint_data = {
            "novel_info": {
                "title": title,
                "genre": genre,
                "description": description,
                "chapter_count": chapter_count,
                "created_at": datetime.now().isoformat()
            }
        }

        # 尝试从断点恢复
        start_step = 0
        if resume:
            checkpoint = self._load_checkpoint(title)
            if checkpoint:
                logger.info(f"发现断点，从 Step {checkpoint['step']} 恢复")
                blueprint_data = checkpoint.get("data", blueprint_data)
                start_step = checkpoint["step"]
                self.checkpoint_data = checkpoint

        try:
            # Step 1: 生成世界观地图
            if start_step <= 0:
                self._update_progress(title, 1, "world_map", "generating", "正在生成世界观地图...")
                logger.info(f"Step 1: 生成世界观地图 - {title}")
                world_map = await self._generate_world_map(title, genre, description, chapter_count)
                blueprint_data["world_map"] = world_map
                self._save_checkpoint(title, 1, blueprint_data)
                self._update_progress(title, 1, "world_map", "completed", "世界观地图生成完成")
            elif "world_map" not in blueprint_data:
                # 断点数据不完整，重新生成
                self._update_progress(title, 1, "world_map", "generating", "重新生成世界观地图...")
                logger.info(f"Step 1: 重新生成世界观地图")
                world_map = await self._generate_world_map(title, genre, description, chapter_count)
                blueprint_data["world_map"] = world_map
                self._save_checkpoint(title, 1, blueprint_data)
                self._update_progress(title, 1, "world_map", "completed", "世界观地图生成完成")

            # Step 2: 生成宏观规划
            if start_step <= 1:
                self._update_progress(title, 2, "macro_plot", "generating", f"正在生成 {chapter_count} 章宏观规划...")
                logger.info(f"Step 2: 生成 {chapter_count} 章宏观规划")
                macro_plot = await self._generate_macro_plot(title, genre, blueprint_data["world_map"], chapter_count)
                blueprint_data["macro_plot"] = macro_plot
                self._save_checkpoint(title, 2, blueprint_data)
                self._update_progress(title, 2, "macro_plot", "completed", "宏观规划生成完成")
            elif "macro_plot" not in blueprint_data:
                self._update_progress(title, 2, "macro_plot", "generating", "重新生成宏观规划...")
                logger.info(f"Step 2: 重新生成宏观规划")
                macro_plot = await self._generate_macro_plot(title, genre, blueprint_data["world_map"], chapter_count)
                blueprint_data["macro_plot"] = macro_plot
                self._save_checkpoint(title, 2, blueprint_data)
                self._update_progress(title, 2, "macro_plot", "completed", "宏观规划生成完成")

            # Step 3: 生成人物体系
            if start_step <= 2:
                self._update_progress(title, 3, "character_system", "generating", "正在生成人物体系...")
                character_system = await self._generate_character_system(title, genre, blueprint_data["world_map"], blueprint_data["macro_plot"])
                blueprint_data["character_system"] = character_system
                self._save_checkpoint(title, 3, blueprint_data)
                self._update_progress(title, 3, "character_system", "completed", "人物体系生成完成")
            elif "character_system" not in blueprint_data:
                self._update_progress(title, 3, "character_system", "generating", "重新生成人物体系...")
                logger.info(f"Step 3: 重新生成人物体系")
                character_system = await self._generate_character_system(title, genre, blueprint_data["world_map"], blueprint_data["macro_plot"])
                blueprint_data["character_system"] = character_system
                self._save_checkpoint(title, 3, blueprint_data)
                self._update_progress(title, 3, "character_system", "completed", "人物体系生成完成")

            # Step 4: 生成伏笔网络
            if start_step <= 3:
                self._update_progress(title, 4, "hook_network", "generating", "正在生成伏笔网络...")
                logger.info(f"Step 4: 生成伏笔网络")
                hook_network = await self._generate_hook_network(title, blueprint_data["world_map"], blueprint_data["macro_plot"])
                blueprint_data["hook_network"] = hook_network
                self._save_checkpoint(title, 4, blueprint_data)
                self._update_progress(title, 4, "hook_network", "completed", "伏笔网络生成完成")
            elif "hook_network" not in blueprint_data:
                self._update_progress(title, 4, "hook_network", "generating", "重新生成伏笔网络...")
                logger.info(f"Step 4: 重新生成伏笔网络")
                hook_network = await self._generate_hook_network(title, blueprint_data["world_map"], blueprint_data["macro_plot"])
                blueprint_data["hook_network"] = hook_network
                self._save_checkpoint(title, 4, blueprint_data)
                self._update_progress(title, 4, "hook_network", "completed", "伏笔网络生成完成")

            # Step 5: 整合蓝图
            self._update_progress(title, 5, "blueprint", "generating", "正在整合蓝图...")
            blueprint = {
                **blueprint_data,
                "status": "completed",
                "completion_time": datetime.now().isoformat()
            }

            # 清除断点
            self._clear_checkpoint(title)

            self.state = "idle"
            self._update_progress(title, 5, "blueprint", "completed", "蓝图创建完成！")
            logger.info(f"蓝图创建完成：{title}")
            return blueprint

        except Exception as e:
            logger.error(f"创建蓝图失败：{e}")
            self.state = "error"
            self._update_progress(title, -1, "error", "error", f"创建失败：{str(e)}")
            # 保存当前进度
            self._save_checkpoint(title, start_step, blueprint_data)
            return {
                "status": "error",
                "error": str(e),
                "checkpoint_saved": True,
                "resume_from_step": start_step,
                "partial_data": blueprint_data
            }

    def get_checkpoint_status(self, title: str) -> Optional[Dict[str, Any]]:
        """获取断点状态"""
        checkpoint = self._load_checkpoint(title)
        if checkpoint:
            return {
                "exists": True,
                "step": checkpoint.get("step", 0),
                "step_name": checkpoint.get("step_name", "unknown"),
                "timestamp": checkpoint.get("timestamp"),
                "title": checkpoint.get("title")
            }
        return {"exists": False}

    def delete_checkpoint(self, title: str) -> bool:
        """删除断点"""
        self._clear_checkpoint(title)
        return True
    
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
        """生成宏观规划 - 分批生成避免超时"""
        # 计算需要生成多少卷（每卷约 20 章）
        volumes_count = max(5, chapter_count // 20)  # 至少 5 卷

        # 只生成前 5 卷的详细规划，避免一次性生成太多
        prompt = f"""你是一位专业的长篇规划师。为小说《{title}》生成前 5 卷的规划。

总章节数：{chapter_count} 章（本次只规划前 5 卷）
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

        response = await self._call_llm(prompt, max_tokens=2000)

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
    
    async def _call_llm(self, prompt: str, max_tokens: int = 4000, use_stream: bool = None) -> str:
        """调用 LLM API - 带重试机制和流式响应支持"""
        if not self.llm_client:
            raise Exception("LLM 未配置")

        api_key = self.llm_client['api_key']
        base_url = self.llm_client['base_url']
        endpoint = self.llm_client.get('endpoint', '/v1/chat/completions')
        model = self.llm_client['model']
        timeout = self.llm_client.get('timeout', 600)  # 默认 10 分钟

        # 从配置读取是否使用流式响应（默认 True，本地 LLM 可设为 False）
        if use_stream is None:
            use_stream = self.llm_client.get('use_stream', True)

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
            'temperature': 0.7,
            'stream': use_stream  # 启用流式响应
        }

        # 重试机制：最多重试 3 次
        last_error = None
        for attempt in range(3):
            try:
                logger.info(f"LLM API 调用中... (尝试 {attempt+1}/3, 流式: {use_stream})")

                if use_stream:
                    # 流式响应模式 - 避免长时间等待断开
                    return await self._call_llm_stream(base_url, endpoint, headers, payload, timeout)
                else:
                    # 非流式模式（备用）
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(
                            f"{base_url}{endpoint}",
                            headers=headers,
                            json={**payload, 'stream': False}
                        )

                        if response.status_code == 200:
                            data = response.json()
                            content = data['choices'][0]['message']['content']
                            logger.info(f"LLM API 调用成功，返回长度：{len(content)}")
                            return content
                        else:
                            error_msg = f"LLM API 调用失败：{response.status_code}"
                            logger.error(error_msg)
                            last_error = Exception(error_msg)
                            if attempt < 2:
                                logger.info("等待 3 秒后重试...")
                                await asyncio.sleep(3)
            except httpx.TimeoutException as e:
                logger.error(f"LLM API 超时（尝试 {attempt+1}/3）: {e}")
                last_error = e
                if attempt < 2:
                    logger.info("等待 5 秒后重试...")
                    await asyncio.sleep(5)
            except httpx.ReadError as e:
                logger.error(f"网络读取错误（尝试 {attempt+1}/3）: {e}")
                last_error = e
                if attempt < 2:
                    logger.info("等待 5 秒后重试...")
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"LLM API 调用异常（尝试 {attempt+1}/3）: {e}")
                last_error = e
                if attempt < 2:
                    logger.info("等待 3 秒后重试...")
                    await asyncio.sleep(3)

        # 所有重试都失败
        raise Exception(f"LLM 调用失败，重试 3 次后仍失败：{last_error}")

    async def _call_llm_stream(self, base_url: str, endpoint: str, headers: Dict, payload: Dict, timeout: int) -> str:
        """流式调用 LLM API - 避免超时断开"""
        full_content = []

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{base_url}{endpoint}",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"LLM API 调用失败：{response.status_code} - {error_text[:200]}")

                logger.info("流式响应开始接收...")
                chunk_count = 0

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content_chunk = delta.get('content', '')
                                if content_chunk:
                                    full_content.append(content_chunk)
                                    chunk_count += 1
                                    if chunk_count % 50 == 0:
                                        logger.info(f"已接收 {chunk_count} 个数据块，累计 {len(''.join(full_content))} 字符")
                        except json.JSONDecodeError:
                            continue  # 跳过无效 JSON

        result = ''.join(full_content)
        logger.info(f"流式响应完成，总长度：{len(result)}")
        return result


# ========== 全自动创作系统 ==========

class AutoCreationSystem:
    """
    全自动创作系统
    一键生成完整小说设定和章节
    支持断点续传
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
        chapter_count: int = 3000,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        从零开始创建小说（全自动）- 支持断点续传

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

        Args:
            resume: 是否从断点恢复
        """

        logger.info(f"开始全自动创作：{title} (断点续传: {resume})")

        # Step 1: 创建蓝图（支持断点续传）
        self.blueprint = await self.architect.create_novel_blueprint(
            title, genre, description, chapter_count, resume=resume
        )

        if self.blueprint.get('status') == 'error':
            return self.blueprint
        
        # Step 2: 保存蓝图到数据库
        from app.novel_db import get_novel_database
        db = get_novel_database()

        # 创建小说
        novel_id = db.create_novel(title, genre, description)

        # 保存蓝图到数据库
        blueprint_settings = {
            "world_map": self.blueprint.get("world_map", {}),
            "macro_plot": self.blueprint.get("macro_plot", {}),
            "character_system": self.blueprint.get("character_system", {}),
            "hook_network": self.blueprint.get("hook_network", {}),
            "chapter_count": chapter_count,
            "blueprint_created_at": datetime.now().isoformat()
        }
        db.update_novel_settings(novel_id, blueprint_settings)
        logger.info(f"[OK] 蓝图已保存到数据库：{novel_id}")

        # Step 3: 生成第一章（带错误处理）
        try:
            first_chapter = await self._generate_first_chapter(novel_id, self.blueprint)

            return {
                "status": "success",
                "novel_id": novel_id,
                "blueprint": self.blueprint,
                "first_chapter": first_chapter
            }
        except Exception as e:
            logger.error(f"生成第一章失败：{e}")
            # 返回部分成功结果（蓝图已完成）
            return {
                "status": "partial_success",
                "novel_id": novel_id,
                "blueprint": self.blueprint,
                "error": f"蓝图创建成功，但第一章生成失败：{str(e)}",
                "can_resume": True
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


def get_auto_creation_system(llm_client: Dict[str, Any] = None) -> AutoCreationSystem:
    """获取全自动创作系统单例

    Args:
        llm_client: 可选的 LLM 客户端配置。如果未提供，从数据库加载
    """
    global _creation_system
    if _creation_system is None:
        if llm_client is None:
            # 从数据库加载配置
            from app.config_db import get_config_database
            db = get_config_database()

            default_provider = db.get_default_provider()
            provider_config = db.get_provider(default_provider)

            if provider_config and provider_config.get('api_key'):
                llm_client = {
                    'api_key': provider_config['api_key'],
                    'base_url': provider_config['base_url'],
                    'model': provider_config['model'],
                    'timeout': provider_config.get('timeout', 300)
                }
            else:
                raise Exception("LLM 未配置")

        _creation_system = AutoCreationSystem(llm_client)

    return _creation_system
