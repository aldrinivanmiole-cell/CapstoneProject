import sqlite3
conn = sqlite3.connect('school.db')
c = conn.cursor()
c.execute('PRAGMA table_info(questions)')
columns = c.fetchall()
print('Questions table columns:')
for col in columns:
    print(f'  {col[1]}: {col[2]} ({col[3]})')
c.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="questions"')
result = c.fetchone()
print('Table creation SQL:')
print(result[0] if result else 'Not found')
conn.close()