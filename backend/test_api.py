import requests
import json

print('=== 测试全自动创作 API ===\n')

r = requests.post(
    'http://localhost:8000/api/auto/create',
    json={
        'title': '测试字数',
        'genre': '玄幻',
        'description': '测试',
        'chapter_count': 20
    },
    timeout=300
)

print(f"状态码：{r.status_code}")
result = r.json()
print(f"\n返回结果:")
print(json.dumps(result, ensure_ascii=False, indent=2))
