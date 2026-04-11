import os
import sqlite3

print("当前目录:", os.getcwd())
print("原始数据库文件是否存在:", os.path.exists("data/contest_trace_raw.db"))

if os.path.exists("data/contest_trace_raw.db"):
    print("原始数据库文件大小:", os.path.getsize("data/contest_trace_raw.db"), "字节")
    
    try:
        conn = sqlite3.connect("data/contest_trace_raw.db")
        print("原始数据库连接成功")
        
        cursor = conn.cursor()
        
        # 查看表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"原始数据库中的表: {tables}")
        
        # 检查raw_notices表的结构
        if 'raw_notices' in [table[0] for table in tables]:
            cursor.execute("PRAGMA table_info(raw_notices);")
            columns = cursor.fetchall()
            print("raw_notices表字段:")
            for column in columns:
                print(f"- {column[1]} ({column[2]})")
            
            # 检查缺失的ID
            missing_ids = [694, 733, 1230]
            for rid in missing_ids:
                cursor.execute("SELECT id, title FROM raw_notices WHERE id = ?", (rid,))
                result = cursor.fetchone()
                if result:
                    print(f"原始ID {rid}: {result[1]}")
                else:
                    print(f"原始ID {rid} 不存在于原始数据库中")
        else:
            print("raw_notices表不存在")
        
        conn.close()
        print("原始数据库连接已关闭")
        
    except Exception as e:
        print(f"错误: {e}")
else:
    print("原始数据库文件不存在")
