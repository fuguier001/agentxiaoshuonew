# ==========================================
# 多 Agent 协作小说系统 - 学习分析师 Agent
# 第 7 大 Agent：负责分析作品、学习技巧、优化风格
# ==========================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import httpx
import json

logger = logging.getLogger(__name__)


class LearningAgent:
    """
    学习分析师 Agent
    
    职责:
    1. 分析已完成章节的质量
    2. 学习优秀作品的写作技巧
    3. 提取作者风格特征
    4. 优化后续章节创作
    5. 提供写作建议和改进方向
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.llm_client = config.get('llm_client')
        self.memory_engine = config.get('memory_engine')
        self.state = "idle"
        self.last_active = None
    
    async def analyze_chapter_quality(
        self,
        content: str,
        chapter_num: int,
        prev_chapters: List[Dict],
        world_map: Optional[Dict] = None,
        protagonist_halo: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """分析章节质量"""
        
        prompt = f"""你是一位专业的学习分析师。请分析以下章节的质量。

【章节内容】
{content[:5000]}...

【章节信息】
第{chapter_num}章

【前 3 章内容】（用于对比进步）
"""
        for ch in prev_chapters[-3:]:
            prompt += f"第{ch['chapter_num']}章：{ch.get('content', '')[:500]}...\n\n"
        
        prompt += """
【分析维度】

## 1. 文笔质量（0-10 分）
- 语言流畅度
- 描写生动性
- 对话自然度
- 节奏把控

## 2. 爽点设计（0-10 分）
- 爽点密度（每多少字一个爽点）
- 爽点类型（打脸/装逼/收获/美人/升级）
- 爽点合理性
- 读者情绪调动

## 3. 人物塑造（0-10 分）
- 主角性格展现
- 配角形象刻画
- 人物关系发展
- 角色弧光

## 4. 剧情设计（0-10 分）
- 情节紧凑度
- 冲突设计
- 伏笔埋设
- 悬念设置

## 5. 金手指使用（0-10 分）
- 是否符合等级设定
- 是否遵守限制
- 是否体现副作用
- 爽点贡献度

## 6. 改进建议
- 最大优点（3 个）
- 最大缺点（3 个）
- 具体改进方向

请用 JSON 格式输出：
```json
{
  "scores": {
    "writing": 0,
    "cool_points": 0,
    "character": 0,
    "plot": 0,
    "halo_usage": 0,
    "overall": 0
  },
  "highlights": ["优点 1", "优点 2", "优点 3"],
  "weaknesses": ["缺点 1", "缺点 2", "缺点 3"],
  "suggestions": ["建议 1", "建议 2", "建议 3"],
  "cool_point_analysis": {
    "density": "每 X 字一个爽点",
    "types": ["打脸", "装逼"],
    "effectiveness": "效果评价"
  },
  "writing_style": {
    "tone": "文风（轻松/严肃/热血）",
    "pace": "节奏（快/中/慢）",
    "focus": "重点（剧情/人物/世界观）"
  }
}
```

请开始分析："""
        
        return await self._call_llm(prompt, max_tokens=3000)
    
    async def extract_writing_style(self, chapters: List[Dict]) -> Dict[str, Any]:
        """提取作者写作风格"""
        
        # 准备章节内容
        content_sample = ""
        for ch in chapters[-5:]:  # 最近 5 章
            content_sample += ch.get('content', '')[:1000] + "...\n\n"
        
        prompt = f"""你是一位专业的写作风格分析师。请分析以下章节的写作风格。

【章节样本】
{content_sample[:5000]}...

【分析维度】

## 1. 叙事风格
- 视角（第一人称/第三人称）
- 叙事节奏（快/中/慢）
- 描写重点（动作/心理/环境）

## 2. 语言特色
- 文风（轻松/严肃/热血/幽默）
- 词汇偏好（古风/现代/混搭）
- 句式特点（长句/短句/混合）

## 3. 爽点设计偏好
- 常用爽点类型
- 爽点铺垫方式
- 爽点爆发节奏

## 4. 人物塑造风格
- 主角性格类型
- 配角塑造方式
- 关系发展模式

## 5. 剧情设计风格
- 常用情节套路
- 冲突设计偏好
- 伏笔埋设习惯

请用 JSON 格式输出：
```json
{
  "narrative": {
    "pov": "视角",
    "pace": "节奏",
    "focus": "重点"
  },
  "language": {
    "style": "文风",
    "vocabulary": "词汇偏好",
    "sentence": "句式特点"
  },
  "cool_points": {
    "types": ["常用爽点类型"],
    "setup": "铺垫方式",
    "payoff": "爆发节奏"
  },
  "characters": {
    "protagonist_type": "主角类型",
    "supporting_style": "配角塑造",
    "relationship_pattern": "关系模式"
  },
  "plot": {
    "tropes": ["常用套路"],
    "conflict_style": "冲突风格",
    "hook_pattern": "伏笔模式"
  }
}
```

请开始分析："""
        
        return await self._call_llm(prompt, max_tokens=3000)
    
    async def generate_writing_suggestions(
        self,
        quality_analysis: Dict[str, Any],
        style_profile: Dict[str, Any],
        target_improvements: List[str]
    ) -> Dict[str, Any]:
        """生成写作改进建议"""
        
        prompt = f"""你是一位专业的写作导师。请根据以下分析生成具体的写作改进建议。

【章节质量分析】
{json.dumps(quality_analysis, ensure_ascii=False, indent=2)}

【写作风格档案】
{json.dumps(style_profile, ensure_ascii=False, indent=2)}

【目标改进方向】
{', '.join(target_improvements) if target_improvements else '全面提升'}

请生成详细的改进建议：

## 1. 短期改进（下一章就可以做）
- 具体技巧（3-5 个）
- 实施方法
- 预期效果

## 2. 中期改进（10-50 章内）
- 需要练习的技巧
- 建议阅读的作品
- 练习方法

## 3. 长期改进（100 章以上）
- 需要培养的能力
- 推荐学习的作家
- 成长路径

## 4. 爽点设计优化
- 当前爽点密度分析
- 建议的爽点频率
- 新的爽点类型建议

## 5. 人物塑造优化
- 主角塑造建议
- 配角塑造建议
- 人物关系发展建议

## 6. 节奏控制优化
- 当前节奏分析
- 建议的节奏调整
- 高潮分布建议

请用 JSON 格式输出：
```json
{
  "short_term": [
    {"skill": "技巧名", "method": "实施方法", "expected": "预期效果"}
  ],
  "mid_term": [
    {"skill": "技巧名", "practice": "练习方法", "resources": "推荐资源"}
  ],
  "long_term": [
    {"ability": "能力名", "mentor": "推荐作家", "path": "成长路径"}
  ],
  "cool_points": {
    "current_density": "当前密度",
    "suggested_density": "建议密度",
    "new_types": ["新爽点类型"]
  },
  "characters": {
    "protagonist": "主角建议",
    "supporting": "配角建议",
    "relationships": "关系发展建议"
  },
  "pacing": {
    "current": "当前节奏",
    "suggested": "建议节奏",
    "climax_distribution": "高潮分布"
  }
}
```

请开始生成建议："""
        
        return await self._call_llm(prompt, max_tokens=4000)
    
    async def learn_from_excellent_works(
        self,
        genre: str,
        excellent_chapters: List[str],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """从优秀作品中学习"""
        
        prompt = f"""你是一位专业的写作分析师。请从以下优秀作品中学习写作技巧。

【小说类型】
{genre}

【优秀章节样本】
"""
        for i, chapter in enumerate(excellent_chapters[:3], 1):
            prompt += f"\n【样本{i}】\n{chapter[:1500]}...\n"
        
        prompt += f"""
【重点学习领域】
{', '.join(focus_areas) if focus_areas else '全面学习'}

请分析并提取可学习的技巧：

## 1. 开篇技巧
- 如何吸引读者
- 如何引入主角
- 如何设置悬念

## 2. 爽点设计
- 爽点类型
- 铺垫方式
- 爆发时机
- 读者情绪调动

## 3. 人物塑造
- 主角登场方式
- 性格展现技巧
- 配角塑造方法

## 4. 节奏控制
- 章节节奏
- 情节推进速度
- 高潮设计

## 5. 对话技巧
- 对话风格
- 信息传递方式
- 性格体现

## 6. 可借鉴的具体技巧
- 可以直接使用的技巧（3-5 个）
- 需要改编的技巧（3-5 个）
- 需要注意的陷阱

请用 JSON 格式输出：
```json
{
  "opening_techniques": [
    {"name": "技巧名", "description": "说明", "example": "示例"}
  ],
  "cool_point_design": [
    {"type": "爽点类型", "setup": "铺垫方法", "payoff": "爆发方式"}
  ],
  "character_development": [
    {"aspect": "塑造方面", "technique": "技巧", "application": "应用方法"}
  ],
  "pacing_control": [
    {"element": "节奏元素", "method": "控制方法", "effect": "效果"}
  ],
  "dialogue_skills": [
    {"skill": "对话技巧", "usage": "使用场景", "example": "示例"}
  ],
  "actionable_tips": [
    {"tip": "具体技巧", "difficulty": "难度", "priority": "优先级"}
  ]
}
```

请开始分析学习："""
        
        return await self._call_llm(prompt, max_tokens=5000)
    
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
                {'role': 'system', 'content': '你是一位专业的学习分析师，擅长分析作品质量、提取写作风格、生成改进建议。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        for attempt in range(3):
            try:
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
                        if attempt < 2:
                            await asyncio.sleep(5)
                        else:
                            raise Exception(f"LLM API 调用失败：{response.status_code}")
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    raise
        
        raise Exception("LLM 调用失败，已达最大重试次数")


# ========== 全局单例 ==========

_learning_agent: Optional[LearningAgent] = None


def get_learning_agent() -> LearningAgent:
    """获取学习分析师 Agent 单例"""
    global _learning_agent
    if _learning_agent is None:
        from app.utils.llm_client import get_llm_client
        from app.memory.memory_engine import get_memory_engine
        
        llm_client = get_llm_client()
        memory_engine = get_memory_engine()
        
        config = {
            'llm_client': llm_client,
            'memory_engine': memory_engine
        }
        
        _learning_agent = LearningAgent('learning_agent', config)
    
    return _learning_agent
