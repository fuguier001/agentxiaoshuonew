from app.novel_db import get_novel_database

db = get_novel_database()

# 获取所有小说
novels = db.get_all_novels()
print(f'Total novels: {len(novels)}\n')

# 更新每个小说的统计信息
for novel in novels:
    novel_id = novel['id']
    db._update_novel_stats(novel_id)
    
    # 重新获取更新后的统计
    updated = db.get_novel(novel_id)
    print(f'{updated["title"]}: {updated["total_chapters"]} chapters, {updated["total_words"]} words')
