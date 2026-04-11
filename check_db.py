import sqlite3

# 连接原始数据库
try:
    conn = sqlite3.connect('data/contest_trace_raw.db')
    print('数据库连接成功')
    
    cursor = conn.cursor()
    
    # 检查raw_notices表
    print('\n检查raw_notices表中的数据:')
    
    # 检查记录数
    cursor.execute('SELECT COUNT(*) FROM raw_notices')
    count = cursor.fetchone()[0]
    print(f'记录数: {count}')
    
    # 检查特定ID
    missing_ids = [694, 733, 1230]
    for rid in missing_ids:
        cursor.execute('SELECT id, title FROM raw_notices WHERE id = ?', (rid,))
        result = cursor.fetchone()
        if result:
            print(f'ID {rid}: {result[1]}')
        else:
            print(f'ID {rid}: Not found')
    
    # 检查ID范围
    cursor.execute('SELECT MIN(id), MAX(id) FROM raw_notices')
    min_max = cursor.fetchone()
    print(f'ID范围: {min_max[0]} - {min_max[1]}')
    
    conn.close()
    print('\n数据库连接已关闭')
except Exception as e:
    print('Error:', e)
