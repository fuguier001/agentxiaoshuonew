from app.workflow_executor import WritingWorkflowExecutor

print('=== 测试 workflow_executor 初始化 ===\n')

executor = WritingWorkflowExecutor()

print(f"llm_client: {executor.llm_client}")

if executor.llm_client:
    print(f"✅ LLM 配置加载成功")
    print(f"   API Key: {executor.llm_client['api_key'][:20]}...")
    print(f"   Base URL: {executor.llm_client['base_url']}")
else:
    print(f"❌ LLM 配置加载失败")
