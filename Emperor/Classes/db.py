import sqlite3

database = sqlite3.connect("xp.db")

Cursor = database.cursor()
result = Cursor.execute("SELECT name FROM sqlite_master")
print(result.fetchone())

result = Cursor.execute("""
    INSERT INTO player VALUES 
                        ('Player1', 1, 5)
                        ('Sata', 2, 10)
""")

database.commit()

for row in Cursor.execute("SELECT year, title FROM movie ORDER BY year"):
    print(row)