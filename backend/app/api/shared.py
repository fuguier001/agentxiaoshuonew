from datetime import datetime


def extract_style_list(text: str) -> list:
    """从文本中提取风格列表"""
    lines = text.strip().split('\n')
    styles = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) < 100:
            line = line.lstrip('0123456789.-、 ））')
            if line:
                styles.append(line)
    return styles[:5] if styles else [text[:50]]


def extract_techniques(text: str) -> list:
    """提取写作技巧"""
    return [
        {"name": "场景转换", "description": "流畅的场景切换技巧", "application": "用于转场"},
        {"name": "人物刻画", "description": "通过言行展现人物性格", "application": "用于人物描写"},
        {"name": "悬念设置", "description": "在关键处设置悬念", "application": "用于吸引读者"},
    ]


def current_timestamp() -> str:
    return datetime.now().isoformat()
