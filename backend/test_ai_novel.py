import httpx
import json
import asyncio

async def create_chapter():
    print("=" * 70)
    print("多 Agent 协作小说系统 - 真实创作测试")
    print("=" * 70)

    with open("config/llm_providers.json", "r") as f:
        config = json.load(f)

    providers = config.get("providers", {})
    provider = providers.get("eggfans", {})

    api_key = provider.get('api_key', '')
    base_url = provider.get('base_url', '')
    model = provider.get('model', '')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient(timeout=300.0) as client:

        # ========== 第一章 ==========
        print("\n" + "=" * 70)
        print("第一章：星海召唤")
        print("=" * 70)

        prompt1 = """你是一位专业的小说作家。

请为小说《星际迷途》创作第一章，约1500字。

背景：公元2150年，人类已经实现星际航行。主角李明，24岁，天体物理学博士候选人。

写出完整第一章，要有：
1. 引人入胜的开场
2. 主角李明的出场
3. 神秘信号的发现
4. 悬念钩子

直接输出小说正文。"""

        payload1 = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的小说作家。'},
                {'role': 'user', 'content': prompt1}
            ],
            'max_tokens': 2500,
            'temperature': 0.8
        }

        print("正在创作第一章，请稍候...")
        response1 = await client.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload1)

        if response1.status_code == 200:
            data1 = response1.json()
            chapter1 = data1['choices'][0]['message']['content']
            print(f"\n第一章完成！字数：{len(chapter1)} 字")
            print("\n" + "-" * 70)
            print(chapter1)
            print("-" * 70)
        else:
            print(f"第一章创作失败: {response1.text}")

        # ========== 第二章 ==========
        print("\n\n" + "=" * 70)
        print("第二章：深空信号")
        print("=" * 70)

        prompt2 = """继续小说《星际迷途》第二章，约1500字。

上文：李明发现来自织女星系的异常信号，信号呈现某种规律性。

请创作第二章，要有：
1. 李明继续研究信号
2. 国际科学界的反应
3. 新的悬念

直接输出小说正文。"""

        payload2 = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的小说作家。'},
                {'role': 'user', 'content': prompt2}
            ],
            'max_tokens': 2500,
            'temperature': 0.8
        }

        print("正在创作第二章，请稍候...")
        response2 = await client.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload2)

        if response2.status_code == 200:
            data2 = response2.json()
            chapter2 = data2['choices'][0]['message']['content']
            print(f"\n第二章完成！字数：{len(chapter2)} 字")
            print("\n" + "-" * 70)
            print(chapter2)
            print("-" * 70)
        else:
            print(f"第二章创作失败: {response2.text}")

        # ========== 第三章 ==========
        print("\n\n" + "=" * 70)
        print("第三章：星际议会")
        print("=" * 70)

        prompt3 = """继续小说《星际迷途》第三章，约1500字。

上文：地球联合政府成立特别委员会研究信号，李明被任命为核心成员。

请创作第三章，要有：
1. 李明参加委员会
2. 政治势力的博弈
3. 更大阴谋浮现

直接输出小说正文。"""

        payload3 = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的小说作家。'},
                {'role': 'user', 'content': prompt3}
            ],
            'max_tokens': 2500,
            'temperature': 0.8
        }

        print("正在创作第三章，请稍候...")
        response3 = await client.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload3)

        if response3.status_code == 200:
            data3 = response3.json()
            chapter3 = data3['choices'][0]['message']['content']
            print(f"\n第三章完成！字数：{len(chapter3)} 字")
            print("\n" + "-" * 70)
            print(chapter3)
            print("-" * 70)
        else:
            print(f"第三章创作失败: {response3.text}")

        print("\n\n" + "=" * 70)
        print("测试完成！")
        print("=" * 70)

asyncio.run(create_chapter())
