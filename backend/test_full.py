import requests
import json
import time

print('=== 完整测试全自动创作流程 ===\n')

start = time.time()

try:
    r = requests.post(
        'http://localhost:8000/api/auto/create',
        json={
            'title': '最终测试',
            'genre': '玄幻',
            'description': '测试用',
            'chapter_count': 20
        },
        timeout=300
    )
    
    elapsed = time.time() - start
    
    print(f"耗时：{elapsed:.2f}秒\n")
    print(f"状态码：{r.status_code}\n")
    
    result = r.json()
    print(f"返回状态：{result['status']}")
    print(f"消息：{result.get('message', 'N/A')}\n")
    
    if result['status'] == 'success':
        data = result['data']
        print(f"小说 ID: {data['novel_id']}")
        
        # 检查 blueprint
        bp = data.get('blueprint', {})
        print(f"\nBlueprint 状态：{bp.get('status', 'N/A')}")
        
        # 检查 first_chapter
        fc = data.get('first_chapter', {})
        print(f"\n第一章状态：{fc.get('status', 'N/A')}")
        print(f"第一章消息：{fc.get('message', 'N/A')}")
        
        if fc.get('status') == 'success':
            print(f"第一章字数：{fc.get('word_count', 0)}")
            content = fc.get('content', '')
            if content:
                print(f"\n内容预览（前 100 字）:")
                print(f"{content[:100]}...")
        else:
            print(f"\n❌ 第一章生成失败")
    else:
        print(f"\n❌ 创作失败：{result.get('error', '未知错误')}")
        
except requests.exceptions.Timeout:
    print(f"❌ 请求超时（{elapsed:.2f}秒）")
except Exception as e:
    print(f"❌ 错误：{e}")
