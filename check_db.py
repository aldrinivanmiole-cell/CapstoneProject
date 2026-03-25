import sqlite3
conn = sqlite3.connect('school.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM questions')
print('Total questions:', c.fetchone()[0])
c.execute('SELECT COUNT(*) FROM questions WHERE wrong_minigame IS NOT NULL AND wrong_minigame != ""')
print('Questions with wrong_minigame:', c.fetchone()[0])
c.execute('SELECT wrong_minigame, COUNT(*) FROM questions WHERE wrong_minigame IS NOT NULL AND wrong_minigame != "" GROUP BY wrong_minigame')
print('Minigame distribution:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]}')
conn.close()