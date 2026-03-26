import requests
import json
import time

print('='*60)
print('测试全自动创作 - 监控章节保存')
print('='*60)

start = time.time()

try:
    r = requests.post(
        'http://localhost:8000/api/auto/create',
        json={
            'title': '测试章节保存',
            'genre': '玄幻',
            'description': '测试用',
            'chapter_count': 1
        },
        timeout=600
    )
    
    elapsed = time.time() - start
    
    print(f'\n耗时：{elapsed:.2f}秒 ({elapsed/60:.1f}分钟)\n')
    print(f'状态码：{r.status_code}\n')
    
    result = r.json()
    print(f'返回状态：{result["status"]}')
    print(f'消息：{result.get("message", "N/A")}\n')
    
    if result['status'] == 'success':
        data = result['data']
        novel_id = data['novel_id']
        print(f'小说 ID: {novel_id}\n')
        
        # 检查 first_chapter
        fc = data.get('first_chapter', {})
        print(f'=== 第一章状态 ===')
        print(f'状态：{fc.get("status", "N/A")}')
        print(f'消息：{fc.get("message", "N/A")[:200] if fc.get("message") else "N/A"}')
        print(f'字数：{fc.get("word_count", 0)}')
        
        # 检查数据库
        print(f'\n=== 检查数据库 ===')
        r2 = requests.get(f'http://localhost:8000/api/novels/{novel_id}/chapters')
        chapters = r2.json()['data']['chapters']
        print(f'数据库章节数：{len(chapters)}')
        
        if chapters:
            for ch in chapters:
                content_len = len(ch.get('content', '') or '')
                print(f'  第{ch["chapter_num"]}章：{ch.get("word_count", 0)}字 (实际内容：{content_len}字)')
                if content_len > 0:
                    print(f'    内容预览：{ch["content"][:100]}...')
        else:
            print(f'[FAIL] 数据库中没有章节记录！')
    else:
        print(f'[FAIL] 创作失败')
        print(f'错误：{result.get("error", "未知错误")}')
        
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
