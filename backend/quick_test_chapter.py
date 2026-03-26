import requests
import json
import time

print('='*60)
print('快速测试 - 单章创作（简化工作流）')
print('='*60)

start = time.time()

try:
    r = requests.post(
        'http://localhost:8000/api/auto/create',
        json={
            'title': '快速测试',
            'genre': '玄幻',
            'description': '测试简化工作流',
            'chapter_count': 1
        },
        timeout=300  # 5 分钟超时
    )
    
    elapsed = time.time() - start
    
    print(f'\n耗时：{elapsed:.2f}秒 ({elapsed/60:.1f}分钟)\n')
    print(f'状态码：{r.status_code}\n')
    
    result = r.json()
    print(f'返回状态：{result["status"]}')
    
    if result['status'] == 'success':
        fc = result['data'].get('first_chapter', {})
        print(f'\n第一章状态：{fc.get("status", "N/A")}')
        
        if fc.get('status') == 'success':
            print(f'[SUCCESS] 第一章生成成功！')
            print(f'字数：{fc.get("word_count", 0)}')
            print(f'步骤：{fc.get("stages_completed", 0)}/{fc.get("total_stages", 0)}')
        else:
            print(f'[FAIL] 第一章生成失败')
            print(f'错误：{fc.get("message", "未知错误")}')
    else:
        print(f'[FAIL] 创作失败')
        
except Exception as e:
    print(f'[ERROR] {e}')
