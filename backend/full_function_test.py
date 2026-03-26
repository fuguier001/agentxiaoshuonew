import requests
import json

print('='*60)
print('全面功能审查')
print('='*60)

tests_passed = 0
tests_failed = 0

def test(name, func):
    global tests_passed, tests_failed
    try:
        result = func()
        if result:
            print(f'[OK] {name}')
            tests_passed += 1
        else:
            print(f'[FAIL] {name}')
            tests_failed += 1
    except Exception as e:
        print(f'[ERROR] {name}: {e}')
        tests_failed += 1

# 测试 1: API 健康检查
def test_health():
    r = requests.get('http://localhost:8000/api/health/live', timeout=5)
    return r.status_code == 200

# 测试 2: 配置加载
def test_config():
    r = requests.get('http://localhost:8000/api/config', timeout=5)
    config = r.json()
    return config['data']['default_provider'] == 'eggfans' and config['data']['providers']['eggfans']['api_key']

# 测试 3: 小说列表
def test_novels_list():
    r = requests.get('http://localhost:8000/api/novels', timeout=5)
    novels = r.json()['data']['novels']
    return len(novels) > 0

# 测试 4: 小说详情
def test_novel_detail():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    if not novels:
        return False
    r = requests.get(f'http://localhost:8000/api/novels/{novels[0]["id"]}', timeout=5)
    return r.status_code == 200

# 测试 5: 章节列表
def test_chapters_list():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    if not novels:
        return False
    r = requests.get(f'http://localhost:8000/api/novels/{novels[0]["id"]}/chapters', timeout=5)
    return r.status_code == 200

# 测试 6: 章节内容
def test_chapter_content():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    if not novels:
        return False
    r = requests.get(f'http://localhost:8000/api/novels/{novels[0]["id"]}/chapters', timeout=5)
    chapters = r.json()['data']['chapters']
    if not chapters:
        return False
    # 检查是否有内容
    has_content = any(ch.get('content') for ch in chapters)
    return has_content

# 测试 7: 模板列表
def test_templates():
    r = requests.get('http://localhost:8000/api/ai/templates', timeout=5)
    templates = r.json()['data']
    total = sum(len(v) for v in templates.values())
    return total >= 10

# 测试 8: AI 大纲生成
def test_ai_outline():
    r = requests.post(
        'http://localhost:8000/api/ai/generate-outline',
        json={'title': '测试', 'genre': '玄幻', 'description': '测试', 'template_id': 'qichengzhuanhe'},
        timeout=120
    )
    return r.status_code == 200 and r.json()['status'] == 'success'

# 测试 9: 小说创建
def test_novel_create():
    r = requests.post(
        'http://localhost:8000/api/novels',
        json={'title': '功能测试', 'genre': '玄幻', 'description': '测试用'},
        timeout=10
    )
    return r.status_code == 200 and r.json()['status'] == 'success'

# 测试 10: 章节创建
def test_chapter_create():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    test_novel = next((n for n in novels if n['title'] == '功能测试'), None)
    if not test_novel:
        return False
    r = requests.post(
        f'http://localhost:8000/api/novels/{test_novel["id"]}/chapters',
        json={'chapter_num': 1, 'title': '测试章节', 'outline': '测试大纲'},
        timeout=10
    )
    return r.status_code == 200 and r.json()['status'] == 'success'

# 测试 11: 章节更新
def test_chapter_update():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    test_novel = next((n for n in novels if n['title'] == '功能测试'), None)
    if not test_novel:
        return False
    r = requests.put(
        f'http://localhost:8000/api/novels/{test_novel["id"]}/chapters/1',
        json={'content': '测试内容', 'title': '测试章节', 'outline': '测试大纲', 'status': 'draft'},
        timeout=10
    )
    return r.status_code == 200 and r.json()['status'] == 'success'

# 测试 12: 小说更新
def test_novel_update():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    test_novel = next((n for n in novels if n['title'] == '功能测试'), None)
    if not test_novel:
        return False
    r = requests.put(
        f'http://localhost:8000/api/novels/{test_novel["id"]}',
        json={'title': '功能测试 - 已更新', 'genre': '玄幻', 'description': '测试用 - 已更新', 'status': 'ongoing'},
        timeout=10
    )
    return r.status_code == 200 and r.json()['status'] == 'success'

# 测试 13: 小说删除
def test_novel_delete():
    novels = requests.get('http://localhost:8000/api/novels').json()['data']['novels']
    test_novel = next((n for n in novels if '功能测试' in n['title']), None)
    if not test_novel:
        return False
    r = requests.delete(f'http://localhost:8000/api/novels/{test_novel["id"]}', timeout=10)
    return r.status_code == 200 and r.json()['status'] == 'success'

# 执行测试
print('\n=== API 功能测试 ===\n')
test('API 健康检查', test_health)
test('配置加载', test_config)
test('小说列表', test_novels_list)
test('小说详情', test_novel_detail)
test('章节列表', test_chapters_list)
test('章节内容', test_chapter_content)
test('模板列表', test_templates)
test('AI 大纲生成', test_ai_outline)
test('小说创建', test_novel_create)
test('章节创建', test_chapter_create)
test('章节更新', test_chapter_update)
test('小说更新', test_novel_update)
test('小说删除', test_novel_delete)

print(f'\n{"="*60}')
print(f'测试结果：通过 {tests_passed}/{tests_passed + tests_failed}')
print(f'{"="*60}')

if tests_failed == 0:
    print('\n[SUCCESS] 所有功能正常！')
else:
    print(f'\n[WARNING] {tests_failed} 个功能失败')
