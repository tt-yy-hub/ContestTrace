import sqlite3

# 连接原始数据库
try:
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 检查ID 694
    cursor.execute('SELECT title FROM raw_notices WHERE id = 694')
    result = cursor.fetchone()
    print('ID 694:', result[0] if result else 'Not found')
    
    # 检查ID 733
    cursor.execute('SELECT title FROM raw_notices WHERE id = 733')
    result = cursor.fetchone()
    print('ID 733:', result[0] if result else 'Not found')
    
    # 检查ID 1230
    cursor.execute('SELECT title FROM raw_notices WHERE id = 1230')
    result = cursor.fetchone()
    print('ID 1230:', result[0] if result else 'Not found')
    
    conn.close()
except Exception as e:
    print('Error:', e)
