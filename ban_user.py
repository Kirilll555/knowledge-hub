import sys
import sqlite3
from datetime import datetime, timedelta

user_id = int(sys.argv[1])
reason = sys.argv[2]
minutes = int(sys.argv[3])

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

banned_until = datetime.now() + timedelta(minutes=minutes)

cursor.execute("""
    UPDATE main_profile 
    SET is_banned = 1, 
        ban_reason = ?, 
        banned_at = ?,
        banned_until = ?
    WHERE user_id = ?
""", (reason, datetime.now(), banned_until, user_id))

conn.commit()
conn.close()

print(f"✅ Пользователь {user_id} забанен до {banned_until}")