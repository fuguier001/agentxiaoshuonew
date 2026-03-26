import requests

r = requests.get('http://localhost:8000/api/novels')
novels = r.json()['data']['novels']
print(f'Total novels: {len(novels)}\n')

for i, n in enumerate(novels[:10]):
    print(f'{i+1}. {n["title"]}')
    print(f'   Chapters: {n.get("total_chapters", 0)}, Words: {n.get("total_words", 0)}')
