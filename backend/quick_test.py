import requests
import json
import sys

# 设置控制台编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

print('=== 快速测试 LLM 调用 ===\n')

# 测试 1: 检查配置
print('测试 1: 检查配置')
r = requests.get('http://localhost:8000/api/config')
config = r.json()
print(f"默认提供商：{config['data']['default_provider']}")
has_key = bool(config['data']['providers']['eggfans']['api_key'])
print(f"eggfans 配置：{'[OK]' if has_key else '[FAIL]'}\n")

# 测试 2: 简单 LLM 调用
print('测试 2: 简单 LLM 调用')
try:
    r = requests.post(
        'http://localhost:8000/api/ai/generate-outline',
        json={
            'title': '测试',
            'genre': '玄幻',
            'description': '测试',
            'template_id': 'qichengzhuanhe'
        },
        timeout=120  # 增加到 120 秒
    )
    print(f"状态码：{r.status_code}")
    print(f"返回内容：{r.text[:500]}")
    result = r.json()
    print(f"解析结果：{result}")
except Exception as e:
    print(f"错误：{e}")
