import sqlite3

# 连接原始数据库
conn = sqlite3.connect("data/contest_trace_raw.db")
cursor = conn.cursor()

# 检查缺失的ID
missing_ids = [694, 733, 1230]
for rid in missing_ids:
    cursor.execute("SELECT title FROM notices WHERE id = ?", (rid,))
    result = cursor.fetchone()
    if result:
        print(f"原始ID {rid}: {result[0]}")
    else:
        print(f"原始ID {rid} 不存在于原始数据库中")

conn.close()
