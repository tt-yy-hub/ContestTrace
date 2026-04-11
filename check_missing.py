import sqlite3

print("开始检查缺失的赛事...")

try:
    conn = sqlite3.connect("data/competiton.db")
    print("数据库连接成功")
    
    cursor = conn.cursor()
    
    # 查看表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"数据库中的表: {tables}")
    
    if tables:
        table_name = tables[0][0]
        print(f"使用表: {table_name}")
        
        # 查看字段
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("表字段:")
        for column in columns:
            print(f"- {column[1]}")
        
        # 检查缺失的ID
        missing_ids = [694, 733, 1230]
        for rid in missing_ids:
            cursor.execute(f"SELECT id FROM {table_name} WHERE raw_notice_id = ?", (rid,))
            result = cursor.fetchone()
            if result:
                print(f"[OK] 原始ID {rid} 已筛入")
            else:
                print(f"[MISS] 原始ID {rid} 缺失")
    else:
        print("数据库中没有表")
        
except Exception as e:
    print(f"错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        print("数据库连接已关闭")

