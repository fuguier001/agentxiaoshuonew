# ==========================================
# 快速测试第一章修复
# ==========================================

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.novel_db import get_novel_database
from app.workflow_executor import get_workflow_executor


async def test_simple():
    """简化测试"""
    print("=" * 60)
    print("快速测试：第一章内容生成")
    print("=" * 60)
    
    db = get_novel_database()
    executor = get_workflow_executor()
    
    # 检查 LLM 配置
    if not executor.llm_client:
        print("\n❌ LLM 未配置！")
        print("   请先在配置页面设置 API Key")
        return False
    
    print(f"\n[OK] LLM 配置正常")
    print(f"   提供商：{executor.llm_client.get('model', 'unknown')}")
    print(f"   Base URL: {executor.llm_client.get('base_url', 'unknown')}")
    
    # 创建测试小说
    novel_id = db.create_novel('快速测试', '玄幻', '测试内容')
    print(f"\n[1/3] 创建小说：{novel_id}")
    
    # 创建章节
    db.create_chapter(novel_id, 1, "第一章", "测试大纲")
    print(f"[2/3] 创建章节记录")
    
    # 生成内容
    print(f"[3/3] 调用 AI 生成内容 (这可能需要 2-5 分钟)...")
    result = await executor.execute_chapter_workflow(
        novel_id=novel_id,
        chapter_num=1,
        outline="主角登场，展示世界观",
        word_count_target=2000
    )
    
    print(f"\n   状态：{result.get('status')}")
    print(f"   字数：{result.get('word_count', 0)}")
    
    content = result.get('content', '')
    
    if result.get('status') == 'success' and content and len(content) > 500:
        print(f"\n✅ 内容生成成功！")
        print(f"   实际字数：{len(content)}")
        print(f"   前 200 字：{content[:200]}...")
        
        # 保存到数据库
        db.update_chapter(novel_id, 1, content=content, status='published')
        
        # 验证数据库
        chapter = db.get_chapter(novel_id, 1)
        print(f"\n[验证] 数据库保存:")
        print(f"   字数：{chapter['word_count']}")
        
        if chapter['word_count'] > 500:
            print(f"\n🎉 测试通过！修复有效！")
            return True
    
    print(f"\n❌ 测试失败")
    print(f"   content length: {len(content) if content else 0}")
    print(f"   message: {result.get('message', 'N/A')}")
    return False


if __name__ == '__main__':
    result = asyncio.run(test_simple())
    sys.exit(0 if result else 1)
