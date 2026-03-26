import asyncio
from app.workflow_executor import WritingWorkflowExecutor

async def test_executor():
    print('=== 测试 workflow_executor ===\n')
    
    executor = WritingWorkflowExecutor()
    
    print(f'llm_client: {executor.llm_client}')
    
    if executor.llm_client:
        print(f'[OK] LLM 配置加载成功')
        print(f'   API Key: {executor.llm_client["api_key"][:20]}...')
        print(f'   Base URL: {executor.llm_client["base_url"]}')
        print(f'   Model: {executor.llm_client["model"]}')
    else:
        print(f'[FAIL] LLM 配置加载失败')
        return
    
    # 测试 execute_chapter_workflow
    print('\n=== 测试 execute_chapter_workflow ===')
    result = await executor.execute_chapter_workflow(
        novel_id='test_001',
        chapter_num=1,
        outline='主角初次接触修仙',
        word_count_target=1000
    )
    
    print(f'\n状态：{result["status"]}')
    print(f'消息：{result.get("message", "N/A")[:200] if result.get("message") else "N/A"}')
    
    if result['status'] == 'success':
        print(f'\n[OK] 章节生成成功！')
        print(f'字数：{result.get("word_count", 0)}')
        content = result.get('content', '')
        if content:
            print(f'\n内容预览（前 200 字）:')
            print(content[:200])
            print('...')
    else:
        print(f'\n[FAIL] 章节生成失败')

asyncio.run(test_executor())
