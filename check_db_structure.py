import sqlite3

conn = sqlite3.connect("data/competiton.db")
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"- {table[0]}")

# 查看表结构
if tables:
    table_name = tables[0][0]
    print(f"\n表 {table_name} 的结构:")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]} ({column[2]})")

conn.close()
