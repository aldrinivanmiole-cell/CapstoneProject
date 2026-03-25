import sqlite3
conn = sqlite3.connect('school.db')
cursor = conn.cursor()
cursor.execute('SELECT id, question_text, wrong_minigame FROM questions WHERE wrong_minigame IS NOT NULL AND wrong_minigame != "" ORDER BY id DESC LIMIT 10')
results = cursor.fetchall()
print('Questions with wrong_minigame set:')
for row in results:
    print(f'ID: {row[0]}, Minigame: "{row[2]}", Question: {row[1][:30]}...')
conn.close()