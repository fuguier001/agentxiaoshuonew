import requests
import time
import json

print('=== 真实测试：20 章简化版全自动创作 ===')
print('测试参数:')
print('  书名：都市修仙')
print('  类型：都市修仙')
print('  简介：大学生获得修仙传承')
print('  章节：20 章')
print()

start = time.time()

try:
    r = requests.post(
        'http://localhost:8000/api/auto/create',
        json={
            'title': '都市修仙',
            'genre': '都市修仙',
            'description': '大学生获得修仙传承',
            'chapter_count': 20
        },
        timeout=300
    )
    
    end = time.time()
    
    print(f'\n耗时：{end-start:.2f}秒')
    print('状态:', r.status_code)
    
    result = r.json()
    print('结果:', result['status'])
    print('消息:', result.get('message', '无')[:200])
    
    data = result.get('data', {})
    print('\n=== 生成结果 ===')
    print('小说 ID:', data.get('novel_id'))
    
    bp = data.get('blueprint', {})
    print('世界观:', '✓' if bp.get('world_map') else '✗')
    print('规划:', '✓' if bp.get('macro_plot') else '✗')
    print('人物:', '✓' if bp.get('character_system') else '✗')
    print('第一章:', '✓' if data.get('first_chapter') else '✗')
    
    if bp.get('world_map'):
        print('\n=== 世界观预览 ===')
        print(json.dumps(bp['world_map'], ensure_ascii=False, indent=2)[:500])
    
except Exception as e:
    end = time.time()
    print(f'\n错误：{e}')
    print(f'耗时：{end-start:.2f}秒')
