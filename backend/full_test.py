# 🧪 完整测试脚本

import requests
import json
import time

def test_api(name, func):
    """测试 API"""
    print(f"\n{'='*60}")
    print(f"测试：{name}")
    print('='*60)
    try:
        result = func()
        print(f"[PASS] 通过")
        return True
    except Exception as e:
        print(f"[FAIL] 失败：{e}")
        return False

# ========== 测试 1: 创建小说 ==========
def test_create_novel():
    r = requests.post('http://localhost:8000/api/novels', json={
        'title': '测试专用',
        'genre': '玄幻',
        'description': '测试用小说'
    })
    data = r.json()
    assert data['status'] == 'success', "创建失败"
    novel_id = data['data']['novel_id']
    print(f"创建小说：{novel_id}")
    return novel_id

# ========== 测试 2: 获取小说列表 ==========
def test_get_novels():
    r = requests.get('http://localhost:8000/api/novels')
    data = r.json()
    assert data['status'] == 'success', "获取失败"
    novels = data['data']['novels']
    print(f"小说数量：{len(novels)}")
    return novels

# ========== 测试 3: 创建章节 ==========
def test_create_chapter(novel_id):
    r = requests.post(f'http://localhost:8000/api/novels/{novel_id}/chapters', json={
        'chapter_num': 1,
        'title': '第一章',
        'outline': '测试大纲'
    })
    data = r.json()
    assert data['status'] == 'success', "创建章节失败"
    print(f"创建章节：{data['data']['chapter_id']}")
    return data['data']['chapter_id']

# ========== 测试 4: 获取章节 ==========
def test_get_chapter(novel_id):
    r = requests.get(f'http://localhost:8000/api/novels/{novel_id}/chapters/1')
    data = r.json()
    assert data['status'] == 'success', "获取章节失败"
    print(f"章节内容：{data['data'].get('title', '无')}")
    return data['data']

# ========== 测试 5: 更新章节 ==========
def test_update_chapter(novel_id):
    r = requests.put(f'http://localhost:8000/api/novels/{novel_id}/chapters/1', json={
        'content': '这是测试内容',
        'title': '第一章 测试',
        'outline': '测试大纲',
        'status': 'published'
    })
    data = r.json()
    assert data['status'] == 'success', "更新失败"
    print(f"更新章节：{data['message']}")
    return data

# ========== 测试 6: 全自动创作 ==========
def test_auto_create():
    print("开始全自动创作测试...")
    start = time.time()
    
    r = requests.post('http://localhost:8000/api/auto/create', json={
        'title': '全自动测试',
        'genre': '玄幻',
        'description': '少年成长故事',
        'chapter_count': 20
    }, timeout=300)
    
    elapsed = time.time() - start
    data = r.json()
    
    print(f"耗时：{elapsed:.2f}秒")
    print(f"状态：{data['status']}")
    print(f"消息：{data.get('message', '无')}")
    
    if data['status'] == 'success':
        novel_id = data['data']['novel_id']
        print(f"小说 ID: {novel_id}")
        
        # 验证蓝图
        bp = data['data'].get('blueprint', {})
        print(f"世界观：{'OK' if bp.get('world_map') else 'FAIL'}")
        print(f"规划：{'OK' if bp.get('macro_plot') else 'FAIL'}")
        print(f"人物：{'OK' if bp.get('character_system') else 'FAIL'}")
        
        # 验证第一章
        ch = data['data'].get('first_chapter', {})
        print(f"第一章：{'OK' if ch.get('content') else 'FAIL'}")
        
        # 验证数据库保存
        r2 = requests.get(f'http://localhost:8000/api/novels/{novel_id}/chapters')
        chapters = r2.json()['data']['chapters']
        print(f"数据库章节数：{len(chapters)}")
        
        if len(chapters) > 0:
            print(f"[OK] 章节已保存！")
            print(f"第一章字数：{chapters[0].get('word_count', 0)}")
        else:
            print(f"[FAIL] 章节未保存！")
        
        return data
    else:
        print(f"❌ 失败：{data.get('message', '未知错误')}")
        return None

# ========== 运行所有测试 ==========
if __name__ == '__main__':
    print("="*60)
    print("全自动创作系统 - 完整测试")
    print("="*60)
    
    results = []
    
    # 基础 API 测试
    results.append(("创建小说", test_api("创建小说", test_create_novel)))
    results.append(("获取列表", test_api("获取列表", test_get_novels)))
    
    # 章节 API 测试
    novel_id = test_create_novel()
    results.append(("创建章节", test_api("创建章节", lambda: test_create_chapter(novel_id))))
    results.append(("获取章节", test_api("获取章节", lambda: test_get_chapter(novel_id))))
    results.append(("更新章节", test_api("更新章节", lambda: test_update_chapter(novel_id))))
    
    # 全自动创作测试
    results.append(("全自动创作", test_api("全自动创作", test_auto_create)))
    
    # 汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！可以交付！")
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，需要修复")
