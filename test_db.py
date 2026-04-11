import os
import sqlite3

print("当前目录:", os.getcwd())
print("数据库文件是否存在:", os.path.exists("data/competiton.db"))

if os.path.exists("data/competiton.db"):
    print("数据库文件大小:", os.path.getsize("data/competiton.db"), "字节")
    
    try:
        conn = sqlite3.connect("data/competiton.db")
        print("数据库连接成功")
        
        cursor = conn.cursor()
        
        # 尝试执行简单查询
        cursor.execute("SELECT count(*) FROM competition_notices")
        count = cursor.fetchone()[0]
        print(f"竞赛通知数量: {count}")
        
        conn.close()
        print("数据库连接已关闭")
        
    except Exception as e:
        print(f"错误: {e}")
else:
    print("数据库文件不存在")
