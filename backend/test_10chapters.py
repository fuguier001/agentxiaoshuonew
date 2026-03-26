import requests
import json
import time

print('='*60)
print('全自动创作测试 - 10 章小说')
print('='*60)
print()

# 开始创作
start = time.time()

print('开始创作...\n')

try:
    r = requests.post(
        'http://localhost:8000/api/auto/create',
        json={
            'title': '逆天剑神',
            'genre': '玄幻',
            'description': '少年林炎偶得神秘剑魂，从此踏上剑道巅峰。战天骄，灭强敌，一剑破万法，终成剑中至尊！',
            'chapter_count': 10
        },
        timeout=600  # 10 分钟超时
    )
    
    elapsed = time.time() - start
    
    print(f'\n耗时：{elapsed:.2f}秒 ({elapsed/60:.1f}分钟)\n')
    print(f'状态码：{r.status_code}\n')
    
    result = r.json()
    print(f'返回状态：{result["status"]}')
    print(f'消息：{result.get("message", "N/A")}\n')
    
    if result['status'] == 'success':
        data = result['data']
        print(f'小说 ID: {data["novel_id"]}\n')
        
        # 检查 blueprint
        bp = data.get('blueprint', {})
        print('=== Blueprint 状态 ===')
        print(f'状态：{bp.get("status", "N/A")}')
        print(f'世界观：{"[OK]" if bp.get("world_map") else "[FAIL]"}')
        print(f'规划：{"[OK]" if bp.get("macro_plot") else "[FAIL]"}')
        print(f'人物：{"[OK]" if bp.get("character_system") else "[FAIL]"}')
        
        # 检查 first_chapter
        fc = data.get('first_chapter', {})
        print(f'\n=== 第一章状态 ===')
        print(f'状态：{fc.get("status", "N/A")}')
        
        if fc.get('status') == 'success':
            print(f'[SUCCESS] 第一章生成成功！')
            print(f'字数：{fc.get("word_count", 0)}')
            content = fc.get('content', '')
            if content:
                print(f'\n内容预览（前 300 字）:')
                print('-'*60)
                print(content[:300])
                print('...')
                print('-'*60)
        else:
            print(f'[FAIL] 第一章生成失败')
            print(f'错误信息：{fc.get("message", "未知错误")}')
        
        # 验证数据库
        print(f'\n=== 验证数据库 ===')
        novel_id = data['novel_id']
        r2 = requests.get(f'http://localhost:8000/api/novels/{novel_id}/chapters')
        chapters = r2.json()['data']['chapters']
        print(f'数据库章节数：{len(chapters)}')
        
        if chapters:
            for ch in chapters[:3]:
                content_len = len(ch.get('content', '') or '')
                print(f'  第{ch["chapter_num"]}章：{ch.get("word_count", 0)}字 (实际内容：{content_len}字)')
        
        print(f'\n[SUCCESS] 测试完成！')
        
    else:
        print(f'\n[FAIL] 创作失败')
        print(f'错误：{result.get("error", "未知错误")}')
        
except requests.exceptions.Timeout:
    print(f'\n[TIMEOUT] 请求超时（{elapsed:.2f}秒）')
except Exception as e:
    print(f'\n[ERROR] 错误：{e}')
    import traceback
    traceback.print_exc()
