# ==========================================
# 测试第一章内容修复
# 验证内容生成和保存是否正常
# ==========================================

import asyncio
import sys
from pathlib import Path

# 添加 backend 到路径
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.novel_db import get_novel_database
from app.novel_architect import get_auto_creation_system
from app.workflow_executor import get_workflow_executor


async def test_chapter_creation():
    """测试单章创作"""
    print("=" * 60)
    print("测试：单章创作")
    print("=" * 60)
    
    db = get_novel_database()
    executor = get_workflow_executor()
    
    # 创建测试小说
    novel_id = db.create_novel('测试单章创作', '玄幻', '测试单章内容')
    print(f"\n[1/4] 创建小说：{novel_id}")
    
    # 创建章节记录
    db.create_chapter(novel_id, 1, "第一章 测试", "主角登场，展示世界观")
    print(f"[2/4] 创建章节记录")
    
    # 生成章节内容
    print(f"[3/4] 调用 AI 生成章节内容...")
    result = await executor.execute_chapter_workflow(
        novel_id=novel_id,
        chapter_num=1,
        outline="主角登场，展示世界观，第一个小冲突",
        word_count_target=2000
    )
    
    print(f"\n   返回状态：{result.get('status')}")
    print(f"   返回字数：{result.get('word_count', 0)}")
    print(f"   消息：{result.get('message', 'N/A')[:100]}")
    
    # 验证内容
    content = result.get('content', '')
    if result.get('status') == 'success' and content and len(content) > 500:
        print(f"\n[OK] 内容生成成功！实际字数：{len(content)}")
        
        # 保存内容
        db.update_chapter(
            novel_id, 1,
            content=content,
            title="第一章 测试",
            status='published'
        )
        print(f"[4/4] 内容已保存到数据库")
        
        # 验证数据库
        chapter = db.get_chapter(novel_id, 1)
        print(f"\n[验证] 数据库查询:")
        print(f"   章节 ID: {chapter['id']}")
        print(f"   标题：{chapter['title']}")
        print(f"   字数：{chapter['word_count']}")
        print(f"   内容前 100 字：{chapter['content'][:100]}...")
        
        if chapter['word_count'] > 500:
            print(f"\n✅ 测试通过！字数：{chapter['word_count']}")
            return True
        else:
            print(f"\n❌ 测试失败：数据库字数={chapter['word_count']}")
            return False
    else:
        print(f"\n❌ 内容生成失败")
        print(f"   content length: {len(content) if content else 0}")
        return False


async def test_auto_create():
    """测试全自动创作"""
    print("\n" + "=" * 60)
    print("测试：全自动创作")
    print("=" * 60)
    
    try:
        system = get_auto_creation_system()
        
        print(f"\n[1/5] 开始全自动创作...")
        result = await system.create_novel_from_scratch(
            title='全自动测试',
            genre='玄幻',
            description='少年踏上修仙之路',
            chapter_count=3000
        )
        
        print(f"\n[2/5] 返回状态：{result.get('status')}")
        print(f"[3/5] 小说 ID: {result.get('novel_id')}")
        
        if result.get('status') == 'success':
            blueprint = result.get('blueprint', {})
            print(f"[4/5] 蓝图状态：{blueprint.get('status', 'N/A')}")
            
            first_chapter = result.get('first_chapter', {})
            print(f"[5/5] 第一章状态：{first_chapter.get('status', 'N/A')}")
            print(f"   第一章字数：{first_chapter.get('word_count', 0)}")
            
            # 验证数据库
            novel_id = result['novel_id']
            db = get_novel_database()
            chapter = db.get_chapter(novel_id, 1)
            
            if chapter and chapter['word_count'] > 500:
                print(f"\n✅ 全自动创作成功！")
                print(f"   数据库字数：{chapter['word_count']}")
                print(f"   内容前 100 字：{chapter['content'][:100]}...")
                return True
            else:
                print(f"\n⚠️ 全自动创作完成但第一章字数不足")
                print(f"   数据库字数：{chapter['word_count'] if chapter else 0}")
                return False
        else:
            print(f"\n❌ 全自动创作失败：{result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 异常：{e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("第一章内容修复验证测试")
    print("=" * 60)
    
    # 测试 1: 单章创作
    test1_passed = await test_chapter_creation()
    
    # 测试 2: 全自动创作
    test2_passed = await test_auto_create()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"单章创作：{'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"全自动创作：{'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！修复有效！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，需要进一步修复")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
