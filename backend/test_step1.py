import httpx
import asyncio

async def test_workflow_llm():
    api_key = 'sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8HusmDnatZ93U1'
    base_url = 'https://eggfans.com'
    model = 'deepseek-v3.2'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 测试 Step 1: 细化大纲
    prompt = """你是一位专业的剧情架构师。请细化以下章节大纲：

原始大纲：
主角初次接触修仙

要求：
1. 明确本章的核心冲突
2. 列出关键情节点（3-5 个）
3. 说明情感起伏
4. 指出需要埋设的伏笔

请输出细化后的大纲："""
    
    payload = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 2000,
        'temperature': 0.7
    }
    
    print('正在测试 Step 1: 细化大纲...')
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            print(f"状态码：{response.status_code}")
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"[OK] 细化大纲成功！")
                print(f"长度：{len(content)}字")
                print(f"\n内容预览（前 200 字）:")
                print(content[:200])
                print('...')
            else:
                print(f"[FAIL] 错误：{response.text[:200]}")
    except Exception as e:
        print(f"[ERROR] 异常：{e}")

asyncio.run(test_workflow_llm())
