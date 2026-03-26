# 全自动创作测试 - 展示生成质量

import requests
import json
import time

print('='*60)
print('全自动创作测试 - 展示生成质量')
print('='*60)

# 开始创作
print('\n开始创作...')
start = time.time()

r = requests.post(
    'http://localhost:8000/api/auto/create',
    json={
        'title': '仙武帝尊',
        'genre': '玄幻',
        'description': '少年叶辰偶得神秘玉佩，从此踏上修仙之路。战天骄，灭强敌，最终登临武道巅峰',
        'chapter_count': 20
    },
    timeout=300
)

elapsed = time.time() - start
result = r.json()

print(f'\n耗时：{elapsed:.2f}秒')
print(f'状态：{result["status"]}')
print(f'消息：{result.get("message", "")}')

if result['status'] == 'success':
    data = result['data']
    novel_id = data['novel_id']
    
    print(f'\n小说 ID: {novel_id}')
    print('\n' + '='*60)
    print('【世界观】')
    print('='*60)
    
    bp = data.get('blueprint', {})
    world_map = bp.get('world_map', {})
    
    if world_map:
        print(json.dumps(world_map, ensure_ascii=False, indent=2))
    else:
        print('未生成世界观')
    
    print('\n' + '='*60)
    print('【20 章规划】')
    print('='*60)
    
    macro_plot = bp.get('macro_plot', {})
    if macro_plot:
        print(json.dumps(macro_plot, ensure_ascii=False, indent=2))
    else:
        print('未生成规划')
    
    print('\n' + '='*60)
    print('【主角设定】')
    print('='*60)
    
    characters = bp.get('character_system', {})
    if characters:
        print(json.dumps(characters, ensure_ascii=False, indent=2))
    else:
        print('未生成人物')
    
    print('\n' + '='*60)
    print('【第一章内容】')
    print('='*60)
    
    # 从数据库获取第一章
    r2 = requests.get(f'http://localhost:8000/api/novels/{novel_id}/chapters/1')
    chapter = r2.json()
    
    if chapter['status'] == 'success' and chapter['data']:
        ch = chapter['data']
        print(f"标题：{ch.get('title', '无')}")
        print(f"字数：{ch.get('word_count', 0)}")
        print(f"大纲：{ch.get('outline', '无')}")
        print(f"\n正文:\n{ch.get('content', '无内容')[:2000]}")
    else:
        print('第一章内容暂无')
    
    print('\n' + '='*60)
    print('测试完成')
    print('='*60)
else:
    print(f'\n失败：{result.get("message", "未知错误")}')
