import sqlite3
conn = sqlite3.connect('school.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM assignments')
print('Total assignments:', c.fetchone()[0])
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
print('Tables:', [row[0] for row in c.fetchall()])
conn.close()