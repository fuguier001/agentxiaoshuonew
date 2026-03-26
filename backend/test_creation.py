import requests
import json

print('=== 检查全自动创作 API 返回 ===\n')

# 测试全自动创作
print('开始创作测试小说...\n')
r = requests.post(
    'http://localhost:8000/api/auto/create',
    json={
        'title': '测试字数统计',
        'genre': '玄幻',
        'description': '测试用',
        'chapter_count': 20
    },
    timeout=300
)

result = r.json()
print(f"状态：{result['status']}")
print(f"消息：{result.get('message', '')}\n")

if result['status'] == 'success':
    data = result['data']
    print(f"小说 ID: {data['novel_id']}")
    
    # 检查第一章
    first_chapter = data.get('first_chapter', {})
    print(f"\n第一章状态:")
    print(f"  status: {first_chapter.get('status', 'N/A')}")
    print(f"  content 长度：{len(first_chapter.get('content', '') or '')}")
    print(f"  word_count: {first_chapter.get('word_count', 'N/A')}")
    
    if first_chapter.get('content'):
        print(f"\n  内容预览（前 200 字）:")
        print(f"  {first_chapter['content'][:200]}...")
    else:
        print(f"\n  ❌ 内容为空！")
        print(f"  完整返回：{json.dumps(first_chapter, ensure_ascii=False, indent=2)[:500]}")
else:
    print(f"❌ 创作失败：{result.get('error', '未知错误')}")
