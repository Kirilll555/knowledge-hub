import sys
import sqlite3
from datetime import datetime

user_id = sys.argv[1]
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT is_banned, banned_until FROM main_profile WHERE user_id = ?", (user_id,))
row = cursor.fetchone()

if row and row[0] == 1:
    if row[1]:
        banned_until = datetime.fromisoformat(row[1])
        if banned_until > datetime.now():
            print('banned')
        else:
            cursor.execute("UPDATE main_profile SET is_banned = 0, banned_until = NULL WHERE user_id = ?", (user_id,))
            conn.commit()

            cursor.execute("""
                INSERT INTO main_notification (user_id, notification_type, title, message, link, is_read, created_at)
                VALUES (?, 'system', '🔓 Аккаунт разблокирован', 'Ваш аккаунт был автоматически разблокирован по истечении срока бана.', '/', 0, datetime('now'))
            """, (user_id,))
            conn.commit()

            print('not_banned')
    else:
        print('banned')
else:
    print('not_banned')

conn.close()