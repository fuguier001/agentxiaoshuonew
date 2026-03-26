import httpx
import json
import asyncio

async def test_llm():
    print("=" * 60)
    print("测试 LLM API 连接")
    print("=" * 60)

    # 读取配置
    with open("config/llm_providers.json", "r") as f:
        config = json.load(f)

    providers = config.get("providers", {})
    default_provider = config.get("default_provider", "eggfans")

    if default_provider in providers:
        provider = providers[default_provider]
        print(f"\n使用提供商: {default_provider}")
        print(f"API Key: {provider.get('api_key', '')[:20]}...")
        print(f"Base URL: {provider.get('base_url', '')}")
        print(f"Model: {provider.get('model', '')}")

        api_key = provider.get('api_key', '')
        base_url = provider.get('base_url', '')
        model = provider.get('model', '')

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的小说作家。'},
                {'role': 'user', 'content': '请用50字描述一个科幻故事的开场：'}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }

        print("\n正在调用 LLM API...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                )

                print(f"\n响应状态码: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    print(f"\nLLM 输出:\n{content}")
                    print("\n[OK] LLM API 连接成功!")
                else:
                    print(f"\n[FAIL] LLM API 调用失败")

        except Exception as e:
            print(f"\n[FAIL] 错误: {e}")
    else:
        print(f"\n[FAIL] 提供商 {default_provider} 不存在")

asyncio.run(test_llm())
