import requests
import json

print('=== 检查小说数据 ===\n')

# 获取小说列表
r = requests.get('http://localhost:8000/api/novels')
novels = r.json()['data']['novels']
print(f'小说总数：{len(novels)}\n')

for novel in novels[:5]:
    print(f"书名：{novel['title']}")
    print(f"  章节数：{novel.get('total_chapters', 0)}")
    print(f"  总字数：{novel.get('total_words', 0)}")
    
    # 检查章节内容
    chapters_r = requests.get(f"http://localhost:8000/api/novels/{novel['id']}/chapters")
    chapters = chapters_r.json()['data']['chapters']
    print(f"  实际章节数：{len(chapters)}")
    
    if chapters:
        for ch in chapters[:2]:
            content = ch.get('content', '')
            print(f"    第{ch['chapter_num']}章：{ch.get('word_count', 0)}字，内容长度：{len(content) if content else 0}")
    print()
