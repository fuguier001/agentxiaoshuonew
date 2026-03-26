# ==========================================
# 多 Agent 协作小说系统 - 派系管理系统数据库
# ==========================================

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json
import logging
import sqlite3

logger = logging.getLogger(__name__)


class SchoolDatabase:
    """
    派系数据库 - 管理写作派系和风格融合
    """

    _instance: Optional['SchoolDatabase'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._db_path = Path("./data/schools.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._init_default_schools()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                key_features TEXT,
                style_dimensions TEXT,
                writing_rules TEXT,
                prohibited TEXT,
                dialogue_patterns TEXT,
                description_patterns TEXT,
                representative_works TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fused_styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                style_id TEXT UNIQUE NOT NULL,
                style_name TEXT NOT NULL,
                source_schools TEXT,
                compatibility_score REAL,
                style_features TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS school_compatibilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school1_id TEXT NOT NULL,
                school2_id TEXT NOT NULL,
                compatibility_score REAL,
                conflicts TEXT,
                suggestions TEXT,
                UNIQUE(school1_id, school2_id)
            )
        ''')

        cursor.execute("PRAGMA table_info(schools)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'writing_rules' not in columns:
            cursor.execute("ALTER TABLE schools ADD COLUMN writing_rules TEXT")
        if 'prohibited' not in columns:
            cursor.execute("ALTER TABLE schools ADD COLUMN prohibited TEXT")
        if 'dialogue_patterns' not in columns:
            cursor.execute("ALTER TABLE schools ADD COLUMN dialogue_patterns TEXT")
        if 'description_patterns' not in columns:
            cursor.execute("ALTER TABLE schools ADD COLUMN description_patterns TEXT")

        conn.commit()
        conn.close()
        logger.info("派系数据库初始化完成")

    def _init_default_schools(self):
        """初始化默认派系"""
        default_schools = [
            # ========== 武侠派系 ==========
            {
                "school_id": "wuxia_jinyong",
                "name": "金庸派",
                "category": "wuxia",
                "description": "厚重历史感，家国情怀，武功描写细致，人物性格鲜明",
                "key_features": json.dumps(["历史背景厚重", "多线叙事", "武功描写细致", "家国情怀", "人物性格鲜明"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 8, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "violence_level": 6, "philosophical_depth": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "第三人称限定"],
                    "chapter_structure": ["单元故事+主线推进", "每章3000-5000字"],
                    "fight_scenes": ["招式名称富有诗意", "内功心法描写细腻", "战斗过程与心理结合"],
                    "relationship_development": ["从相识到相知再到相欠", "误会-冲突-和解模式"],
                    "world_building": ["依托真实历史朝代", "门派体系完整自洽"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于现代化的语言", "脱离历史背景的设定", "过于血腥暴力的描写"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["半文半白", "符合人物身份", "富有哲理"], ensure_ascii=False),
                "description_patterns": json.dumps(["武功描写注重意境", "山水风景与心境呼应", "服饰器物讲究考据"], ensure_ascii=False),
                "representative_works": json.dumps(["射雕英雄传", "天龙八部", "神雕侠侣", "倚天屠龙记", "笑傲江湖"], ensure_ascii=False)
            },
            {
                "school_id": "wuxia_gulong",
                "name": "古龙派",
                "category": "wuxia",
                "description": "简洁意境流，重氛围轻招式，悬疑感强，对话富有哲理",
                "key_features": json.dumps(["文风简洁", "重意境", "悬疑氛围", "短句有力", "对话哲理"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 3, "dialogue_ratio": 8,
                    "emotional_intensity": 6, "violence_level": 5, "mystery_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称限定", "第一人称"],
                    "chapter_structure": ["短章节", "每章500-1500字", "章节间留白"],
                    "fight_scenes": ["省略招式过程", "注重战前氛围", "结果导向"],
                    "relationship_development": ["点到为止", "酒友知己模式"],
                    "world_building": ["江湖氛围渲染", "门派模糊处理"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["冗长的招式描写", "详细的历史背景", "过于直白的情感表达"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["短句有力", "富有哲理", "留白艺术", "试探性对话"], ensure_ascii=False),
                "description_patterns": json.dumps(["环境氛围渲染", "感官意象并列", "简洁传神"], ensure_ascii=False),
                "representative_works": json.dumps(["多情剑客无情剑", "楚留香传奇", "陆小凤传奇", "陆小凤系列", "绝代双骄"], ensure_ascii=False)
            },
            {
                "school_id": "wuxia_wang",
                "name": "王度庐派",
                "category": "wuxia",
                "description": "悲剧武侠，言情与武侠融合，女性视角细腻，心理描写深入",
                "key_features": json.dumps(["悲剧色彩浓厚", "言情武侠融合", "女性视角", "心理描写"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 4, "description_density": 7, "dialogue_ratio": 6,
                    "emotional_intensity": 9, "violence_level": 4, "romance_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "女性视角"],
                    "chapter_structure": ["情感递进式", "每章2000-4000字"],
                    "fight_scenes": ["点到为止", "武戏文写"],
                    "relationship_development": ["欲爱不能", "命运悲剧", "克制情感"],
                    "world_building": ["现实主义江湖", "注重社会环境"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于理想化的结局", "武功过于夸张", "大团圆结局"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["含蓄内敛", "欲言又止", "心理外化"], ensure_ascii=False),
                "description_patterns": json.dumps(["心理独白", "意象暗示", "环境映衬心境"], ensure_ascii=False),
                "representative_works": json.dumps(["卧虎藏龙", "铁骑银瓶", "霄玉别传"], ensure_ascii=False)
            },

            # ========== 言情派系 ==========
            {
                "school_id": "romance_qiongyao",
                "name": "琼瑶派",
                "category": "romance",
                "description": "细腻情感，诗意对白，爱情至上，唯美浪漫主义",
                "key_features": json.dumps(["情感细腻", "对白诗意", "爱情主题", "心理描写深入", "唯美主义"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 3, "description_density": 7, "dialogue_ratio": 9,
                    "emotional_intensity": 10, "romance_level": 10, "realism_level": 3
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称", "女性视角"],
                    "chapter_structure": ["情感单元式", "每章1500-3000字"],
                    "relationship_development": ["一见钟情模式", "阻碍-冲突-突破", "误会三角恋"],
                    "world_building": ["理想化场景", "唯美环境描写"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于现实的残酷描写", "平淡琐碎的生活细节", "理性的功利爱情"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["诗意化", "情感直白", "第一封情书式", "独白式"], ensure_ascii=False),
                "description_patterns": json.dumps(["感官描写细腻", "自然景物与情感呼应", "唯美主义"], ensure_ascii=False),
                "representative_works": json.dumps(["还珠格格", "情深深雨蒙蒙", "梅花烙", "新月格格", "鬼丈夫"], ensure_ascii=False)
            },
            {
                "school_id": "romance_zhang",
                "name": "张爱玲派",
                "category": "romance",
                "description": "苍凉底色，世情小说，女性视角，细节丰富，讽刺深刻",
                "key_features": json.dumps(["苍凉底色", "世情小说", "女性视角", "讽刺深刻", "细节丰富"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 4, "description_density": 9, "dialogue_ratio": 7,
                    "emotional_intensity": 7, "romance_level": 6, "realism_level": 9
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "女性视角"],
                    "chapter_structure": ["散文化", "意识流穿插"],
                    "relationship_development": ["算计与真情交织", "婚姻是交易", "爱而不得到放手"],
                    "world_building": ["上海香港都市背景", "大家庭缩影"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于理想化的爱情", "单纯善良的女主", "大团圆结局"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["潜台词丰富", "言不由衷", "身份语言差异"], ensure_ascii=False),
                "description_patterns": json.dumps(["细节控", "服饰建筑考究", "色彩运用"], ensure_ascii=False),
                "representative_works": json.dumps(["倾城之恋", "红玫瑰与白玫瑰", "金锁记", "半生缘", "怨女"], ensure_ascii=False)
            },
            {
                "school_id": "romance_jin",
                "name": "金庸言情派",
                "category": "romance",
                "description": "武侠为表言情为里，刻骨铭心至情至性，错过遗憾之美",
                "key_features": json.dumps(["武侠言情融合", "至情至性", "错过遗憾", "刻骨铭心"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 6, "dialogue_ratio": 7,
                    "emotional_intensity": 9, "romance_level": 9, "violence_level": 5
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知"],
                    "chapter_structure": ["武侠情节推进", "情感线暗线"],
                    "relationship_development": ["相识相知错过", "克制隐忍", "生死相许"],
                    "world_building": ["江湖背景", "门派对立"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["爱情凌驾于江湖规则", "直白的情感表达", "轻易得到的爱情"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["身份等级分明", "含蓄内敛", "行动代替语言"], ensure_ascii=False),
                "description_patterns": json.dumps(["武侠动作与情感结合", "景物烘托", "仪式感"], ensure_ascii=False),
                "representative_works": json.dumps(["神雕侠侣", "倚天屠龙记", "飞狐外传", "书剑恩仇录"], ensure_ascii=False)
            },

            # ========== 玄幻仙侠派系 ==========
            {
                "school_id": "xianxia_ermost",
                "name": "烽火戏诸侯派",
                "category": "xianxia",
                "description": "玄幻都市流，设定新颖独特，节奏明快，爽点密集，升级体系完整",
                "key_features": json.dumps(["设定新颖", "节奏明快", "爽点密集", "升级体系", "都市玄幻"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 10, "description_density": 4, "dialogue_ratio": 5,
                    "emotional_intensity": 6, "fantasy_level": 9, "realism_level": 2
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["快节奏", "每章2000-3000字", "章末留钩子"],
                    "world_building": ["力量体系设定", "等级分明", "副本/秘境"],
                    "plot_patterns": ["装逼打脸", "系统流", "签到流", "抽奖流"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["拖沓的节奏", "过于复杂的设定", "长期虐主"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["爽感对白", "打脸式", "系统提示音"], ensure_ascii=False),
                "description_patterns": json.dumps(["力量数据化", "技能炫酷", "特效描写"], ensure_ascii=False),
                "representative_works": json.dumps(["雪中悍刀行", "剑来", "陈情令", "庆余年"], ensure_ascii=False)
            },
            {
                "school_id": "xianxia_hantian",
                "name": "天蚕土豆派",
                "category": "xianxia",
                "description": "废柴逆袭流，升级打怪换地图，学院体系，战斗燃爆",
                "key_features": json.dumps(["废柴逆袭", "学院体系", "升级打怪", "换地图", "战斗燃爆"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 4, "dialogue_ratio": 5,
                    "emotional_intensity": 7, "fantasy_level": 10, "violence_level": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第三人称限定"],
                    "chapter_structure": ["战斗单元", "每章2000字", "战斗占比高"],
                    "world_building": ["斗气大陆", "学院宗门", "地图递进"],
                    "plot_patterns": ["退婚流", "三年之约", "秘境探险", "宗门大比"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["主角长期弱势", "缺乏升级正反馈", "战斗描写拖沓"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["战斗宣言", "嘲讽打脸", "势力介绍"], ensure_ascii=False),
                "description_patterns": json.dumps(["斗气化翼", "技能特效", "战场描写"], ensure_ascii=False),
                "representative_works": json.dumps(["斗破苍穹", "武动乾坤", "大主宰", "元尊"], ensure_ascii=False)
            },
            {
                "school_id": "xianxia_eren",
                "name": "耳根派",
                "category": "xianxia",
                "description": "修仙求道流，心性修炼，法宝炼制，炼丹炼器，长生冒险",
                "key_features": json.dumps(["修仙求道", "心性修炼", "法宝炼制", "长生冒险", "资源争夺"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 6, "dialogue_ratio": 5,
                    "emotional_intensity": 6, "fantasy_level": 10, "philosophical_depth": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时为主"],
                    "point_of_view": ["第三人称限定"],
                    "chapter_structure": ["修仙日常+战斗", "每章2500字"],
                    "world_building": ["修真界层级", "门派势力", "坊市商会"],
                    "plot_patterns": ["奇遇连连", "炼丹突破", "夺宝探险", "势力崛起"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["心魔过易化解", "突破无代价", "无资源压力"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["利益交换", "坊市交易", "切磋请教"], ensure_ascii=False),
                "description_patterns": json.dumps(["灵根属性", "丹药品级", "法宝威能"], ensure_ascii=False),
                "representative_works": json.dumps(["仙逆", "求魔", "我欲封天", "一念永恒", "三寸人间"], ensure_ascii=False)
            },
            {
                "school_id": "fantasy_guojing",
                "name": "都市郭敬明派",
                "category": "fantasy",
                "description": "华丽唯美派，时尚都市，青春疼痛，物质描写细腻，情感浓烈",
                "key_features": json.dumps(["华丽唯美", "时尚都市", "青春疼痛", "物质描写", "情感浓烈"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 9, "dialogue_ratio": 7,
                    "emotional_intensity": 8, "romance_level": 8, "realism_level": 5
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称女性"],
                    "chapter_structure": ["情感片段式", "每章1500-2500字"],
                    "world_building": ["大都市", "名校贵族", "时尚圈"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["粗糙的生活描写", "缺乏时尚元素", "平淡的情感"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["闺蜜对话", "青春誓言", "疼痛独白"], ensure_ascii=False),
                "description_patterns": json.dumps(["名牌物品描写", "唯美意象", "色彩渲染"], ensure_ascii=False),
                "representative_works": json.dumps(["小时代", "幻城", "夏至未至", "悲伤逆流成河"], ensure_ascii=False)
            },
            {
                "school_id": "fantasy_hanhan",
                "name": "韩寒派",
                "category": "fantasy",
                "description": "幽默讽刺，青春气息，个人风格强烈，赛车元素，文艺青年",
                "key_features": json.dumps(["幽默讽刺", "青春气息", "简洁直白", "思想深刻", "文艺腔调"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 5, "dialogue_ratio": 8,
                    "emotional_intensity": 5, "humor_level": 8, "philosophical_depth": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称"],
                    "chapter_structure": ["段子式", "短章节", "每章1000-2000字"],
                    "world_building": ["当代都市", "校园赛车", "文艺圈"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于矫情", "空洞的青春", "无病呻吟"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["冷幽默", "自嘲", "反讽"], ensure_ascii=False),
                "description_patterns": json.dumps(["细节观察", "生活化", "留白艺术"], ensure_ascii=False),
                "representative_works": json.dumps(["三重门", "长安乱", "一座城池", "后青春的方程式", "1988"], ensure_ascii=False)
            },

            # ========== 科幻派系 ==========
            {
                "school_id": "scifi_liu",
                "name": "刘慈欣派",
                "category": "scifi",
                "description": "宏大叙事，科学严谨，人性深刻，想象力爆棚，史诗级科幻",
                "key_features": json.dumps(["宏大叙事", "科学严谨", "人性深刻", "想象丰富", "史诗级"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 6, "description_density": 7, "dialogue_ratio": 4,
                    "emotional_intensity": 6, "sci_level": 10, "philosophical_depth": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "未来时"],
                    "point_of_view": ["第三人称全知", "多视角"],
                    "chapter_structure": ["宏大篇章", "时间跨度大", "每章3000-5000字"],
                    "world_building": ["宇宙尺度", "技术推演严谨", "文明兴衰"],
                    "plot_patterns": ["文明碰撞", "技术奇点", "宇宙社会学"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["软科幻设定", "小情小爱为主", "科学漏洞"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["理性讨论", "思想实验", "文明对话"], ensure_ascii=False),
                "description_patterns": json.dumps(["硬科技描写", "宇宙场景", "宏大景观"], ensure_ascii=False),
                "representative_works": json.dumps(["三体", "流浪地球", "超新星纪元", "球状闪电", "全频带阻塞干扰"], ensure_ascii=False)
            },
            {
                "school_id": "scifi_hexi",
                "name": "郝景芳派",
                "category": "scifi",
                "description": "人文科幻，心理细腻，城市想象，未来社会批判，女性视角",
                "key_features": json.dumps(["人文关怀", "心理细腻", "城市想象", "社会批判", "女性视角"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 7, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "sci_level": 7, "philosophical_depth": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "未来时"],
                    "point_of_view": ["女性视角", "第一人称"],
                    "chapter_structure": ["心理递进", "每章2000字"],
                    "world_building": ["北京城市变形", "未来社会分层"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["纯技术描写", "忽视人文", "宏大叙事忽略个体"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["内心独白", "日常对话", "心理流"], ensure_ascii=False),
                "description_patterns": json.dumps(["城市空间想象", "心理外化", "意象象征"], ensure_ascii=False),
                "representative_works": json.dumps(["北京折叠", "孤独深处", "流浪苍穹", "去远方"], ensure_ascii=False)
            },

            # ========== 悬疑推理派系 ==========
            {
                "school_id": "mystery_dong",
                "name": "东野圭吾派",
                "category": "mystery",
                "description": "社会派推理，人性挖掘，意外结局，情感与推理结合，文笔流畅",
                "key_features": json.dumps(["社会派推理", "人性挖掘", "意外结局", "情感推理融合", "文笔流畅"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 5, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "mystery_level": 9, "logical_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第三人称全知", "多视角"],
                    "chapter_structure": ["谜团铺垫", "线索交织", "结局逆转"],
                    "plot_patterns": ["找出凶手", "动机探索", "社会问题揭示"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于血腥", "不可能犯罪", "忽视动机"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["日常对话", "审讯技巧", "心理博弈"], ensure_ascii=False),
                "description_patterns": json.dumps(["日常场景", "细节线索", "环境氛围"], ensure_ascii=False),
                "representative_works": json.dumps(["白夜行", "嫌疑人X的献身", "解忧杂货店", "恶意", "放学后"], ensure_ascii=False)
            },
            {
                "school_id": "mystery_lu",
                "name": "松本清张派",
                "category": "mystery",
                "description": "社会派推理元老，深刻社会批判，平民视角，文学性强",
                "key_features": json.dumps(["社会批判", "平民视角", "文学性强", "冷静客观", "深刻揭露"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 7, "dialogue_ratio": 5,
                    "emotional_intensity": 6, "mystery_level": 7, "philosophical_depth": 9
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知"],
                    "chapter_structure": ["社会背景铺陈", "犯罪动机追溯", "社会制度批判"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于离奇的手法", "忽视社会背景", "侦探光环过强"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["克制内敛", "社会对话", "阶级差异"], ensure_ascii=False),
                "description_patterns": json.dumps(["社会环境", "平民生活", "制度批判"], ensure_ascii=False),
                "representative_works": json.dumps(["点与线", "零的焦点", "深层动怒", "日本的黑雾"], ensure_ascii=False)
            },
            {
                "school_id": "mystery_agatha",
                "name": "阿加莎派",
                "category": "mystery",
                "description": "古典推理巅峰，密室推理，POV叙事，文字游戏，优雅谋杀",
                "key_features": json.dumps(["古典推理", "密室谋杀", "POV叙事", "文字游戏", "优雅谋杀"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 6, "dialogue_ratio": 7,
                    "emotional_intensity": 5, "mystery_level": 10, "logical_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["多视角POV", "限制性第三人称"],
                    "chapter_structure": ["嫌疑人逐一登场", "线索平等抛出", "终章解谜"],
                    "plot_patterns": ["暴风雨山庄", "一人一句", "最后的排除法"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["血腥暴力", "超自然元素", "侦探开挂"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["优雅英式", "闲聊中套话", "宴会对话"], ensure_ascii=False),
                "description_patterns": json.dumps(["封闭空间", "不在场证明", "生活习惯细节"], ensure_ascii=False),
                "representative_works": json.dumps(["无人生还", "东方快车谋杀案", "尼罗河上的惨案", " ABC谋杀案", "阳光下的罪恶"], ensure_ascii=False)
            },

            # ========== 历史派系 ==========
            {
                "school_id": "history_erue",
                "name": "二月河派",
                "category": "history",
                "description": "清代历史小说，政治斗争，官场文化，帝王传记，宏大细腻结合",
                "key_features": json.dumps(["清代历史", "政治斗争", "官场文化", "帝王传记", "宏大细腻"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 8, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "historical_accuracy": 10, "political_level": 9
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "帝王视角"],
                    "chapter_structure": ["历史事件推进", "人物命运交织", "每章3000-4000字"],
                    "world_building": ["清代官制", "宫廷规矩", "社会风俗"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过度戏说", "历史人物走形", "现代价值观植入"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["官场暗语", "君臣对话", "奏折文体"], ensure_ascii=False),
                "description_patterns": json.dumps(["服饰礼仪", "宫殿建筑", "官制仪轨"], ensure_ascii=False),
                "representative_works": json.dumps(["康熙王朝", "雍正皇帝", "乾隆皇帝", "乾隆朝臣", "少年天子"], ensure_ascii=False)
            },
            {
                "school_id": "history_lu",
                "name": "鲁迅派",
                "category": "history",
                "description": "深刻批判文学，国民性反思，匕首投枪式，文笔精炼，思想深刻",
                "key_features": json.dumps(["国民性批判", "思想深刻", "匕首投枪", "文笔精炼", "忧国忧民"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 4, "description_density": 8, "dialogue_ratio": 5,
                    "emotional_intensity": 7, "philosophical_depth": 10, "satire_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第一人称", "第三人称全知"],
                    "chapter_structure": ["散文式", "短小精悍", "留白艺术"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["空洞说教", "直白表达", "缺乏文学性"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["含蓄讽刺", "潜台词丰富", "沉默力量"], ensure_ascii=False),
                "description_patterns": json.dumps(["白描手法", "典型人物", "环境象征"], ensure_ascii=False),
                "representative_works": json.dumps(["阿Q正传", "狂人日记", "孔乙己", "闰土", "药"], ensure_ascii=False)
            },

            # ========== 恐怖惊悚派系 ==========
            {
                "school_id": "horror_stephen",
                "name": "斯蒂芬金派",
                "category": "horror",
                "description": "心理恐怖大师，日常生活恐怖，人物立体，恐惧源于内心，社会批判",
                "key_features": json.dumps(["心理恐怖", "日常生活恐怖", "人物立体", "恐惧内心", "社会批判"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 8, "dialogue_ratio": 6,
                    "emotional_intensity": 9, "horror_level": 9, "psychological_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["日常铺垫", "恐惧渐增", "高潮爆发"],
                    "horror_sources": ["超自然", "心理疾病", "家庭创伤", "社会暴力"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["纯粹血腥", "无人物深度", "jump scare滥用"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["日常对话", "心理独白", "恐惧描写"], ensure_ascii=False),
                "description_patterns": json.dumps(["感官恐惧", "日常物品恐怖化", "心理扭曲描写"], ensure_ascii=False),
                "representative_works": json.dumps(["闪灵", "肖申克的救赎", "它", "宠物公墓", "迷雾"], ensure_ascii=False)
            },
            {
                "school_id": "horror_yio",
                "name": "乙一派",
                "category": "horror",
                "description": "日本恐怖轻小说，双面风格，白乙一温柔治愈，黑乙一残酷冰冷",
                "key_features": json.dumps(["双面风格", "白乙一治愈", "黑乙一残酷", "短篇见长", "人性挖掘"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 6, "description_density": 6, "dialogue_ratio": 5,
                    "emotional_intensity": 8, "horror_level": 7, "literary_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称", "少年视角"],
                    "chapter_structure": ["短篇为主", "氛围营造", "意外结局"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过度血腥", "说教味", "复杂情节"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["简洁对话", "沉默角色", "独白式"], ensure_ascii=False),
                "description_patterns": json.dumps(["日常恐怖", "孤独意象", "心理距离"], ensure_ascii=False),
                "representative_works": json.dumps(["ZOO", "夏天烟火和我的尸体", "平面国", "GOTH断掌事件", "在黑暗中等"], ensure_ascii=False)
            },

            # ========== 都市派系 ==========
            {
                "school_id": "urban_official",
                "name": "官场职场派",
                "category": "urban",
                "description": "职场政治，权谋斗争，晋升之道，人情世故，写实风格",
                "key_features": json.dumps(["职场政治", "权谋斗争", "晋升之道", "人情世故", "写实风格"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 6, "dialogue_ratio": 8,
                    "emotional_intensity": 6, "political_level": 9, "realism_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["事件单元", "人物成长", "每章2000-3000字"],
                    "world_building": ["机关单位", "企业职场", "权力结构"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于理想化的升职", "忽视人际关系", "主角无敌"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["话里有话", "官场黑话", "请示汇报"], ensure_ascii=False),
                "description_patterns": json.dumps(["办公场景", "人际微妙", "权力结构"], ensure_ascii=False),
                "representative_works": json.dumps(["沧浪之水", "侯卫东官场笔记", "二号首长", "国画", "梅兰藏"], ensure_ascii=False)
            },
            {
                "school_id": "urban_romance",
                "name": "都市言情派",
                "category": "urban",
                "description": "现代都市爱情，霸道总裁，甜宠虐恋，职场碰撞，契约恋爱",
                "key_features": json.dumps(["现代都市", "甜宠虐恋", "霸道总裁", "契约恋爱", "职场言情"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 5, "dialogue_ratio": 9,
                    "emotional_intensity": 8, "romance_level": 10, "realism_level": 4
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时"],
                    "point_of_view": ["女性第一人称", "第三人称"],
                    "chapter_structure": ["甜虐交替", "误会不断", "撒糖与虐心"],
                    "plot_patterns": ["霸道总裁", "契约恋爱", "先婚后爱", "破镜重圆"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于现实的压力", "平淡如水的感情", "缺乏戏剧性"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["撩人台词", "壁咚宣言", "追妻火葬场"], ensure_ascii=False),
                "description_patterns": json.dumps(["豪车豪宅", "霸道行为", "浪漫场景"], ensure_ascii=False),
                "representative_works": json.dumps(["何以笙箫默", "微微一笑很倾城", "何以笙箫默", "杉杉来了", "顾漫系列"], ensure_ascii=False)
            },

            # ========== 军事战争派系 ==========
            {
                "school_id": "military_xuxing",
                "name": "抗战纪实派",
                "category": "military",
                "description": "抗日战争题材，纪实风格，民族情怀，英雄人物，真实历史融合",
                "key_features": json.dumps(["抗战题材", "纪实风格", "民族情怀", "英雄人物", "历史融合"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 7, "description_density": 7, "dialogue_ratio": 6,
                    "emotional_intensity": 8, "violence_level": 7, "patriotic_level": 9
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "多视角"],
                    "chapter_structure": ["战役推进", "人物命运", "每章2500-3500字"],
                    "world_building": ["抗战历史背景", "军事编制", "战场环境"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过度神化主角", "脱离史实", "侮辱英烈"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["军旅语言", "战友情谊", "军民鱼水"], ensure_ascii=False),
                "description_patterns": json.dumps(["战争场面", "武器装备", "战场环境"], ensure_ascii=False),
                "representative_works": json.dumps(["亮剑", "雪豹", "人间正道是沧桑", "我的团长我的团", "生死线"], ensure_ascii=False)
            },
            {
                "school_id": "military_modern",
                "name": "现代军旅派",
                "category": "military",
                "description": "现代军队生活，特种兵题材，热血成长，铁血军魂，科技强军",
                "key_features": json.dumps(["现代军队", "特种兵", "热血成长", "铁血军魂", "科技强军"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 5, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "violence_level": 7, "patriotic_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第三人称限定", "第一人称"],
                    "chapter_structure": ["训练成长", "任务战斗", "每章2000-3000字"],
                    "plot_patterns": ["新兵成长", "特种兵选拔", "国际特种兵大赛", "海外维和"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["违反军队纪律", "过度个人英雄主义", "军旅生活不真实"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["军令如山", "战友黑话", "铁血誓言"], ensure_ascii=False),
                "description_patterns": json.dumps(["武器装备", "战术动作", "训练场面"], ensure_ascii=False),
                "representative_works": json.dumps(["我是特种兵", "利刃出鞘", "特战先锋", "狼牙", "人间冰器"], ensure_ascii=False)
            },

            # ========== 冒险探险派系 ==========
            {
                "school_id": "adventure_lu",
                "name": "盗墓笔记派",
                "category": "adventure",
                "description": "盗墓探险，神秘古墓，粽子机关，文物历史，铁三角情义",
                "key_features": json.dumps(["盗墓探险", "古墓神秘", "粽子机关", "文物历史", "铁三角"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 7, "dialogue_ratio": 7,
                    "emotional_intensity": 7, "mystery_level": 9, "adventure_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时", "过去时"],
                    "point_of_view": ["第一人称", "第三人称"],
                    "chapter_structure": ["探险单元", "古墓解密", "每章2000-3000字"],
                    "world_building": ["神秘古墓", "文物历史", "盗墓流派"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过度恐怖", "文物倒卖美化", "不尊重历史"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["摸金校尉黑话", "队友调侃", "危机时刻誓言"], ensure_ascii=False),
                "description_patterns": json.dumps(["古墓机关", "粽子粽子", "文物器型", "墓室结构"], ensure_ascii=False),
                "representative_works": json.dumps(["盗墓笔记", "鬼吹灯", "黄河鬼棺", "茅山后裔", "我当道士那些年"], ensure_ascii=False)
            },
            {
                "school_id": "adventure_legend",
                "name": "冒险传奇派",
                "category": "adventure",
                "description": "海洋冒险，寻宝探秘，异域风情，个人英雄主义，传奇故事",
                "key_features": json.dumps(["海洋冒险", "寻宝探秘", "异域风情", "个人英雄", "传奇叙事"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 6, "dialogue_ratio": 5,
                    "emotional_intensity": 6, "adventure_level": 10, "exotic_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知"],
                    "chapter_structure": ["冒险单元", "宝藏谜团", "每章2500-3500字"],
                    "world_building": ["海洋岛屿", "异域国家", "宝藏传说"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["不尊重他国文化", "历史虚无主义", "过度奇幻"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["海盗黑话", "冒险宣言", "异域语言"], ensure_ascii=False),
                "description_patterns": json.dumps(["海洋场景", "异域建筑", "宝藏器物"], ensure_ascii=False),
                "representative_works": json.dumps(["海底两万里", "金银岛", "神秘岛", "所罗门王宝藏", "达芬奇密码"], ensure_ascii=False)
            },

            # ========== 轻小说派系 ==========
            {
                "school_id": "lightnovel_jp",
                "name": "日系轻小说派",
                "category": "lightnovel",
                "description": "日本轻小说风格，吐槽文化，萌系角色，学园日常，异世界穿越",
                "key_features": json.dumps(["吐槽文化", "萌系角色", "学园日常", "异世界", "角色互动"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 4, "dialogue_ratio": 9,
                    "emotional_intensity": 6, "humor_level": 8, "fantasy_level": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["日常+事件", "每章1500-2500字", "轻松阅读"],
                    "plot_patterns": ["异世界转生", "学园恋爱", "战斗冒险", "日常治愈"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于沉重", "不尊重角色", "色情擦边"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["内心吐槽", "萌系口癖", "角色特色语言"], ensure_ascii=False),
                "description_patterns": json.dumps(["角色外观描写", "心理吐槽", "场景氛围"], ensure_ascii=False),
                "representative_works": json.dumps(["刀剑神域", "Re:从零开始的异世界生活", "我的青春恋爱物语", "四月是你的谎言", "冰果"], ensure_ascii=False)
            },
            {
                "school_id": "lightnovel_cn",
                "name": "国产轻小说派",
                "category": "lightnovel",
                "description": "国产轻小说风格，中华元素，游戏系统，都市异能，校花倒贴",
                "key_features": json.dumps(["中华元素", "游戏系统", "都市异能", "轻松爽文", "角色互动"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 4, "dialogue_ratio": 8,
                    "emotional_intensity": 6, "humor_level": 8, "fantasy_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时"],
                    "point_of_view": ["第一人称", "第三人称"],
                    "chapter_structure": ["系统任务", "日常互动", "每章2000-3000字"],
                    "plot_patterns": ["系统流", "校花流", "异能流", "直播流"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过度色情", "恶意贬低", "无脑爽文"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["系统提示音", "吐槽对话", "装逼打脸"], ensure_ascii=False),
                "description_patterns": json.dumps(["技能特效", "中华元素", "游戏界面"], ensure_ascii=False),
                "representative_works": json.dumps(["全职高手", "从前有座灵剑山", "奇葩头子", "修真聊天群", "大王饶命"], ensure_ascii=False)
            },

            # ========== 文学派系 ==========
            {
                "school_id": "literary_shen",
                "name": "沈从文派",
                "category": "literary",
                "description": "田园牧歌，湘西风情，自然人性，诗意语言，纯净美好",
                "key_features": json.dumps(["田园牧歌", "湘西风情", "自然人性", "诗意语言", "纯净美好"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 3, "description_density": 9, "dialogue_ratio": 4,
                    "emotional_intensity": 6, "poetic_level": 10, "philosophical_depth": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知", "第一人称"],
                    "chapter_structure": ["散文式", "意象流", "留白艺术"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["城市化描写", "工业元素", "复杂阴谋"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["地方方言", "简洁对话", "含蓄情意"], ensure_ascii=False),
                "description_patterns": json.dumps(["自然风景", "民俗风情", "水墨画意"], ensure_ascii=False),
                "representative_works": json.dumps(["边城", "长河", "湘行散记", "萧萧", "三三"], ensure_ascii=False)
            },
            {
                "school_id": "literary_lu",
                "name": "路遥派",
                "category": "literary",
                "description": "现实主义巨著，城乡交叉地带，奋斗精神，平凡的世界，厚重质朴",
                "key_features": json.dumps(["现实主义", "城乡交叉", "奋斗精神", "平凡世界", "厚重质朴"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 5, "description_density": 8, "dialogue_ratio": 7,
                    "emotional_intensity": 8, "realism_level": 10, "philosophical_depth": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时"],
                    "point_of_view": ["第三人称全知"],
                    "chapter_structure": ["双时间线", "人物群像", "每章3000-4000字"],
                    "world_building": ["陕北农村", "城乡对比", "时代变迁"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["脱离实际的浪漫", "忽视苦难", "不尊重农民"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["陕北方言", "生活对话", "内心独白"], ensure_ascii=False),
                "description_patterns": json.dumps(["黄土地貌", "农活场景", "生活细节"], ensure_ascii=False),
                "representative_works": json.dumps(["平凡的世界", "人生", "在困难的日子里", "我和五叔的六次相遇"], ensure_ascii=False)
            },

            # ========== 网络小说派系 ==========
            {
                "school_id": "webnovel_face_slapping",
                "name": "装逼打脸派",
                "category": "webnovel",
                "description": "网络小说经典流派，主角扮猪吃虎，装逼打脸，爽点密集，节奏飞快",
                "key_features": json.dumps(["扮猪吃虎", "装逼打脸", "爽点密集", "节奏飞快", "正反馈强烈"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 10, "description_density": 3, "dialogue_ratio": 6,
                    "emotional_intensity": 8, "fantasy_level": 8, "爽感_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["每章2000-3000字", "章末留钩子", "装逼打脸单元"],
                    "plot_patterns": ["开局低谷", "奇遇崛起", "打脸反派", "收获美女资源"],
                    "emotional_hooks": ["嘲讽", "打压", "反转", "震撼"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["长期虐主", "主角憋屈", "无脑送装备", "反派无逻辑"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["嘲讽式", "震惊式", "装逼式", "打脸式"], ensure_ascii=False),
                "description_patterns": json.dumps(["技能特效炫酷", "实力碾压", "对手震惊", "环境渲染"], ensure_ascii=False),
                "representative_works": json.dumps(["都市奇门医圣", "都市最强狂兵", "修仙小农民", "上门女婿"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_infinite",
                "name": "无限流派",
                "category": "webnovel",
                "description": "主角穿越不同副本世界完成任务兑换奖励，死亡游戏，极限生存，多元素融合",
                "key_features": json.dumps(["副本世界", "死亡游戏", "任务系统", "极限生存", "多元素融合"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 6, "dialogue_ratio": 5,
                    "emotional_intensity": 9, "fantasy_level": 10, "horror_level": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "限制性第三人称"],
                    "chapter_structure": ["副本单元制", "每章1500-2500字", "死亡边缘"],
                    "plot_patterns": ["副本世界", "任务挑战", "死亡规则", "道具技能", "团队协作"],
                    "world_building": ["主神空间", "副本世界观", "任务类型", "奖励体系"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["副本太简单", "主角无压力", "奖励获取太易", "缺乏紧张感"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["任务提示", "队友配合", "生死对话", "恐怖氛围"], ensure_ascii=False),
                "description_patterns": json.dumps(["恐怖场景", "副本规则", "技能效果", "心理描写"], ensure_ascii=False),
                "representative_works": json.dumps(["无限恐怖", "王牌进化", "死亡开端", "惊悚乐园", "地狱公寓"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_system",
                "name": "系统流派",
                "category": "webnovel",
                "description": "主角获得各类系统辅助，做任务得奖励，升级换奖励，轻松幽默",
                "key_features": json.dumps(["系统辅助", "任务奖励", "升级强化", "轻松幽默", "数据化"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 10, "description_density": 3, "dialogue_ratio": 7,
                    "emotional_intensity": 6, "fantasy_level": 9, "humor_level": 8
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["任务触发", "系统提示", "奖励获取", "每章2000字"],
                    "plot_patterns": ["系统觉醒", "新手任务", "日常任务", "隐藏任务", "成就解锁"],
                    "system_types": ["神级选择", "超级外卖", "神豪系统", "学霸系统", "签到系统"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["系统过于万能", "任务无意义", "奖励太易得", "缺乏挑战"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["系统提示音", "任务播报", "奖励公示", "吐槽对话"], ensure_ascii=False),
                "description_patterns": json.dumps(["系统面板", "属性数据", "技能图标", "包裹空间"], ensure_ascii=False),
                "representative_works": json.dumps(["超级电脑系统", "神级惩罚系统", "万界快递员", "外卖小哥的逆袭", "超级大聘"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_lottery",
                "name": "抽奖流派",
                "category": "webnovel",
                "description": "通过抽奖/开箱获取道具技能，不确定性带来惊喜，运气成分增加戏剧性",
                "key_features": json.dumps(["抽奖开箱", "随机奖励", "惊喜感", "道具收集", "运气成分"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 4, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "fantasy_level": 9, "surprise_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称"],
                    "chapter_structure": ["抽奖单元", "概率事件", "惊喜或失望", "每章2000字"],
                    "plot_patterns": ["抽奖触发", "稀有奖励", "保底机制", "连抽惊喜", "命运逆转"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["奖励太易得", "无失望感", "抽奖无意义", "道具无差异化"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["抽奖播报", "系统提示", "震惊反应", "嘲讽与打脸"], ensure_ascii=False),
                "description_patterns": json.dumps(["抽奖特效", "金色传说", "神级道具", "属性展示"], ensure_ascii=False),
                "representative_works": json.dumps(["我欲称帝", "我的运气又爆表", "超级抽奖系统", "最强运气系统"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_boss",
                "name": "总裁霸道派",
                "category": "webnovel",
                "description": "都市言情经典，女主被男主宠爱，契约恋爱，先婚后爱，甜宠虐恋",
                "key_features": json.dumps(["霸道总裁", "甜宠虐恋", "契约恋爱", "先婚后爱", "女主被宠"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 5, "dialogue_ratio": 9,
                    "emotional_intensity": 9, "romance_level": 10, "realism_level": 3
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时"],
                    "point_of_view": ["女性第一人称", "第三人称"],
                    "chapter_structure": ["甜虐交替", "误会冲突", "撒糖与虐心", "每章1500-2500字"],
                    "plot_patterns": ["误会上错床", "契约结婚", "一夜情带球跑", "霸道壁咚", "追妻火葬场"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["过于现实", "平淡如水", "缺乏霸道", "女主太主动"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["霸总语录", "壁咚宣言", "宠溺对话", "追妻火葬场"], ensure_ascii=False),
                "description_patterns": json.dumps(["豪车豪宅", "霸道动作", "宠溺眼神", "浪漫场景"], ensure_ascii=False),
                "representative_works": json.dumps(["总裁大人放肆宠", "恰似寒光遇骄阳", "萌妻放肆宠", "闪婚总裁太凶猛", "99次爱恋"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_xianxia",
                "name": "玄幻仙侠升级派",
                "category": "webnovel",
                "description": "网络小说仙侠，境界分明，打怪升级，宗门争斗，奇遇连连，逆天改命",
                "key_features": json.dumps(["境界升级", "打怪爆装备", "宗门争斗", "奇遇连连", "逆天改命"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 5, "dialogue_ratio": 5,
                    "emotional_intensity": 7, "fantasy_level": 10, "violence_level": 7
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["过去时为主"],
                    "point_of_view": ["第三人称限定"],
                    "chapter_structure": ["修炼日常", "战斗突破", "每章2000-2500字"],
                    "plot_patterns": ["废物逆袭", "退婚打脸", "奇遇山洞", "宗门大比", "妖兽森林"],
                    "world_building": ["修真境界", "丹药阵法", "法宝灵器", "门派势力"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["境界跳跃太大", "升级太易", "敌人太弱", "奇遇无代价"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["修炼对话", "嘲讽打压", "战斗宣言", "势力介绍"], ensure_ascii=False),
                "description_patterns": json.dumps(["技能特效", "境界威压", "法宝描写", "战场渲染"], ensure_ascii=False),
                "representative_works": json.dumps(["凡人修仙传", "仙逆", "遮天", "完美世界", "盘龙", "星辰变"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_city",
                "name": "都市异能派",
                "category": "webnovel",
                "description": "都市背景超能力，透视读心透视，兵王回归，医术超群，扮猪吃虎",
                "key_features": json.dumps(["都市背景", "异能超能力", "兵王回归", "医术风水", "扮猪吃虎"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 4, "dialogue_ratio": 6,
                    "emotional_intensity": 7, "fantasy_level": 7, "realism_level": 5
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称"],
                    "chapter_structure": ["异能展示", "装逼打脸", "每章2000字"],
                    "plot_patterns": ["兵王回归", "透视眼", "读心术", "医术无双", "风水玄学"],
                    "character_backgrounds": ["特种兵王", "神医传人", "风水世家", "修真者隐世"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["异能过于万能", "毫无代价", "对手太弱", "无成长"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["兵王语录", "打脸对话", "震惊反应", "装逼宣言"], ensure_ascii=False),
                "description_patterns": json.dumps(["异能特效", "都市场景", "豪车美女", "权力描写"], ensure_ascii=False),
                "representative_works": json.dumps(["都市奇门医圣", "透视邪医", "超级兵王", "都市最强狂兵", "都市之最强神医"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_game",
                "name": "游戏异界派",
                "category": "webnovel",
                "description": "现实与游戏世界融合，玩家进入游戏冒险，打怪爆装，副本通关，虚拟网游",
                "key_features": json.dumps(["游戏世界", "打怪升级", "副本通关", "装备技能", "虚拟现实"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 5, "dialogue_ratio": 5,
                    "emotional_intensity": 6, "fantasy_level": 9, "gaming_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称限定"],
                    "chapter_structure": ["游戏任务", "副本挑战", "每章2000字"],
                    "plot_patterns": ["全服第一", "首杀BOSS", "隐藏任务", "神器获取", "公会争霸"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["游戏过于简单", "奖励太易得", "缺乏竞争", "无意义任务"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["游戏提示", "队友语音", "公会频道", "世界广播"], ensure_ascii=False),
                "description_patterns": json.dumps(["游戏界面", "技能特效", "副本场景", "装备属性"], ensure_ascii=False),
                "representative_works": json.dumps(["全职高手", "网游之天下无双", "超神机械师", "神级英雄", "王者荣耀"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_apocalypse",
                "name": "末世囤货派",
                "category": "webnovel",
                "description": "末世降临，丧尸横行，主角重生囤货，建立基地，异能觉醒，生存冒险",
                "key_features": json.dumps(["末世降临", "丧尸横行", "重生囤货", "异能觉醒", "生存冒险"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 8, "description_density": 6, "dialogue_ratio": 5,
                    "emotional_intensity": 8, "horror_level": 8, "survival_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "限制性第三人称"],
                    "chapter_structure": ["末世生存", "丧尸危机", "每章2000字"],
                    "plot_patterns": ["重生先知", "囤积物资", "异能觉醒", "基地建设", "人类幸存"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["物资太易得", "缺乏生存压力", "敌人太弱", "团队无配合"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["末世对话", "危机提示", "团队配合", "物资谈判"], ensure_ascii=False),
                "description_patterns": json.dumps(["丧尸描写", "末世场景", "物资囤积", "异能效果"], ensure_ascii=False),
                "representative_works": json.dumps(["末世囤货流", "末世魔神系统", "我在末世囤积物资", "末世重生之寒潮"], ensure_ascii=False)
            },
            {
                "school_id": "webnovel_travel",
                "name": "诸天万界派",
                "category": "webnovel",
                "description": "穿越诸天万界不同位面影视小说世界，改写命运，收集天道功德，诸天流",
                "key_features": json.dumps(["诸天穿越", "位面跳跃", "影视融合", "改写命运", "天道功德"], ensure_ascii=False),
                "style_dimensions": json.dumps({
                    "narrative_pace": 9, "description_density": 5, "dialogue_ratio": 5,
                    "emotional_intensity": 7, "fantasy_level": 10, "adventure_level": 10
                }, ensure_ascii=False),
                "writing_rules": json.dumps({
                    "allowed_tenses": ["现在时为主"],
                    "point_of_view": ["第一人称", "第三人称"],
                    "chapter_structure": ["位面穿越", "任务挑战", "每章2000字"],
                    "plot_patterns": ["影视世界", "武侠综武", "都市融合", "动漫世界", "洪荒封神"]
                }, ensure_ascii=False),
                "prohibited": json.dumps(["穿越无意义", "任务太简单", "奖励无价值", "缺乏挑战"], ensure_ascii=False),
                "dialogue_patterns": json.dumps(["位面提示", "任务播报", "天道法则", "功德获取"], ensure_ascii=False),
                "description_patterns": json.dumps(["位面描写", "天道功德", "法则之力", "世界规则"], ensure_ascii=False),
                "representative_works": json.dumps(["诸天万界之帝", "诸天万界之最强", "诸天最强综武", "从斗破开始制霸诸天", "诸天最强剑客"], ensure_ascii=False)
            }
        ]

        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        for school in default_schools:
            cursor.execute('''
                INSERT OR IGNORE INTO schools
                (school_id, name, category, description, key_features, style_dimensions,
                 writing_rules, prohibited, dialogue_patterns, description_patterns, representative_works)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['school_id'],
                school['name'],
                school['category'],
                school['description'],
                school['key_features'],
                school['style_dimensions'],
                school.get('writing_rules', '{}'),
                school.get('prohibited', '[]'),
                school.get('dialogue_patterns', '[]'),
                school.get('description_patterns', '[]'),
                school['representative_works']
            ))

        conn.commit()
        conn.close()

    def get_all_schools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有派系"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if category:
                cursor.execute('SELECT * FROM schools WHERE category = ?', (category,))
            else:
                cursor.execute('SELECT * FROM schools')
            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_school_dict(row) for row in rows]

        except Exception as e:
            logger.error(f"获取派系列表失败：{e}")
            return []

    def get_school(self, school_id: str) -> Optional[Dict[str, Any]]:
        """获取派系详情"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM schools WHERE school_id = ?', (school_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_school_dict(row)
            return None

        except Exception as e:
            logger.error(f"获取派系详情失败：{e}")
            return None

    def _row_to_school_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为派系字典"""
        def safe_get(row, key, default=None):
            try:
                return row[key] if key in row.keys() else default
            except:
                return default

        try:
            key_features_str = safe_get(row, 'key_features')
            style_dimensions_str = safe_get(row, 'style_dimensions')
            representative_works_str = safe_get(row, 'representative_works')
            writing_rules_str = safe_get(row, 'writing_rules')
            prohibited_str = safe_get(row, 'prohibited')
            dialogue_patterns_str = safe_get(row, 'dialogue_patterns')
            description_patterns_str = safe_get(row, 'description_patterns')

            key_features = json.loads(key_features_str) if key_features_str else []
            style_dimensions = json.loads(style_dimensions_str) if style_dimensions_str else {}
            representative_works = json.loads(representative_works_str) if representative_works_str else []
            writing_rules = json.loads(writing_rules_str) if writing_rules_str else {}
            prohibited = json.loads(prohibited_str) if prohibited_str else []
            dialogue_patterns = json.loads(dialogue_patterns_str) if dialogue_patterns_str else []
            description_patterns = json.loads(description_patterns_str) if description_patterns_str else []
        except Exception as e:
            logger.error(f"解析派系数据失败：{e}")
            key_features = []
            style_dimensions = {}
            representative_works = []
            writing_rules = {}
            prohibited = []
            dialogue_patterns = []
            description_patterns = []

        return {
            'school_id': safe_get(row, 'school_id'),
            'name': safe_get(row, 'name'),
            'category': safe_get(row, 'category'),
            'description': safe_get(row, 'description'),
            'key_features': key_features,
            'style_dimensions': style_dimensions,
            'writing_rules': writing_rules,
            'prohibited': prohibited,
            'dialogue_patterns': dialogue_patterns,
            'description_patterns': description_patterns,
            'representative_works': representative_works
        }

    def check_compatibility(self, school_ids: List[str]) -> Dict[str, Any]:
        """检查派系兼容性"""
        if len(school_ids) > 3:
            return {
                'compatible': False,
                'score': 0.3,
                'conflicts': ['选择的派系过多，建议不超过3个'],
                'suggestions': ['减少派系数量以提高兼容性']
            }

        if len(school_ids) < 2:
            return {
                'compatible': True,
                'score': 1.0,
                'conflicts': [],
                'suggestions': ['至少选择2个派系进行融合']
            }

        schools = [self.get_school(sid) for sid in school_ids]
        schools = [s for s in schools if s is not None]

        if len(schools) < 2:
            return {
                'compatible': False,
                'score': 0.5,
                'conflicts': ['部分派系不存在'],
                'suggestions': ['请选择有效的派系']
            }

        conflicts = []
        suggestions = []
        total_score = 1.0

        categories = set(s['category'] for s in schools)
        if len(categories) > 2:
            conflicts.append('选择了过多不同类型的派系')
            suggestions.append('同类型派系兼容性更好')
            total_score *= 0.8

        for i, s1 in enumerate(schools):
            for s2 in schools[i+1:]:
                score = self._calculate_pair_compatibility(s1, s2)
                total_score *= score
                if score < 0.6:
                    conflicts.append(f'{s1["name"]}和{s2["name"]}风格差异较大')
                    suggestions.append(f'建议突出{s1["name"]}的某个特征')

        return {
            'compatible': total_score >= 0.6,
            'score': round(total_score, 2),
            'conflicts': conflicts if conflicts else [],
            'suggestions': suggestions if suggestions else ['兼容性良好，可以进行融合']
        }

    def _calculate_pair_compatibility(self, school1: Dict, school2: Dict) -> float:
        """计算两个派系的兼容性"""
        try:
            dim1 = school1.get('style_dimensions', {})
            dim2 = school2.get('style_dimensions', {})

            if not dim1 or not dim2:
                return 0.7

            diff = 0
            for key in dim1:
                if key in dim2:
                    diff += abs(dim1[key] - dim2[key])

            max_diff = len(dim1) * 9
            compatibility = 1 - (diff / max_diff)
            return max(0.3, compatibility)

        except Exception as e:
            logger.error(f"计算兼容性失败：{e}")
            return 0.7

    def fuse_schools(self, school_ids: List[str], fusion_name: str) -> Dict[str, Any]:
        """融合派系"""
        compatibility = self.check_compatibility(school_ids)

        if not compatibility['compatible']:
            return {
                'success': False,
                'error': '派系兼容性不足，无法融合',
                'details': compatibility
            }

        schools = [self.get_school(sid) for sid in school_ids]
        schools = [s for s in schools if s is not None]

        fused_features = []
        fused_dimensions = {
            'narrative_pace': 0,
            'description_density': 0,
            'dialogue_ratio': 0,
            'emotional_intensity': 0
        }

        for school in schools:
            fused_features.extend(school.get('key_features', []))
            for key in fused_dimensions:
                if key in school.get('style_dimensions', {}):
                    fused_dimensions[key] += school['style_dimensions'][key]

        for key in fused_dimensions:
            fused_dimensions[key] = round(fused_dimensions[key] / len(schools), 1)

        style_id = f"fused_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO fused_styles
                (style_id, style_name, source_schools, compatibility_score, style_features)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                style_id,
                fusion_name,
                json.dumps(school_ids, ensure_ascii=False),
                compatibility['score'],
                json.dumps(fused_features[:10], ensure_ascii=False)
            ))

            conn.commit()
            conn.close()

            logger.info(f"融合派系成功：{fusion_name}")

            return {
                'success': True,
                'style_id': style_id,
                'style_name': fusion_name,
                'source_schools': school_ids,
                'compatibility_score': compatibility['score'],
                'style_features': fused_features[:10],
                'style_dimensions': fused_dimensions,
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"融合派系失败：{e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_fused_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        """获取融合风格"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM fused_styles WHERE style_id = ?', (style_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                try:
                    source_schools = json.loads(row['source_schools']) if row['source_schools'] else []
                    style_features = json.loads(row['style_features']) if row['style_features'] else []
                except:
                    source_schools = []
                    style_features = []

                return {
                    'style_id': row['style_id'],
                    'style_name': row['style_name'],
                    'source_schools': source_schools,
                    'compatibility_score': row['compatibility_score'],
                    'style_features': style_features,
                    'created_at': row['created_at']
                }
            return None

        except Exception as e:
            logger.error(f"获取融合风格失败：{e}")
            return None

    def get_all_fused_styles(self) -> List[Dict[str, Any]]:
        """获取所有融合风格"""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM fused_styles ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()

            result = []
            for row in rows:
                try:
                    source_schools = json.loads(row['source_schools']) if row['source_schools'] else []
                    style_features = json.loads(row['style_features']) if row['style_features'] else []
                except:
                    source_schools = []
                    style_features = []

                result.append({
                    'style_id': row['style_id'],
                    'style_name': row['style_name'],
                    'source_schools': source_schools,
                    'compatibility_score': row['compatibility_score'],
                    'style_features': style_features,
                    'created_at': row['created_at']
                })

            return result

        except Exception as e:
            logger.error(f"获取融合风格列表失败：{e}")
            return []

    def delete_fused_style(self, style_id: str) -> bool:
        """删除融合风格"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM fused_styles WHERE style_id = ?', (style_id,))
            conn.commit()
            conn.close()
            logger.info(f"删除融合风格：{style_id}")
            return True
        except Exception as e:
            logger.error(f"删除融合风格失败：{e}")
            return False


_school_db: Optional[SchoolDatabase] = None


def get_school_database() -> SchoolDatabase:
    """获取派系数据库单例"""
    global _school_db
    if _school_db is None:
        _school_db = SchoolDatabase()
    return _school_db