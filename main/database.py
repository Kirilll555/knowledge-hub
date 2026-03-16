# main/database.py
import sqlite3
import os
from django.conf import settings

DB_PATH = os.path.join(settings.BASE_DIR, "db.sqlite3")


def init_profile_table():
    """Создание таблицы profiles, если её нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создаем таблицу (если не существует)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT NOT NULL,
            nickname TEXT,
            age INTEGER,
            school TEXT,
            grade TEXT,
            main_subject TEXT,
            hobby TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Таблица profiles создана или уже существует")


def add_is_guest_column():
    """Добавление колонки is_guest в существующую таблицу"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, существует ли колонка is_guest
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [column[1] for column in cursor.fetchall()]

    if "is_guest" not in columns:
        try:
            cursor.execute("ALTER TABLE profiles ADD COLUMN is_guest INTEGER DEFAULT 0")
            conn.commit()
            print("Колонка is_guest успешно добавлена")
        except Exception as e:
            print(f"Ошибка при добавлении колонки: {e}")
    else:
        print("Колонка is_guest уже существует")

    conn.close()


# Запускаем добавление колонки при импорте
add_is_guest_column()


def save_profile(user_id, username, data):
    """Сохранение или обновление профиля"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE profiles 
            SET nickname = ?, age = ?, school = ?, grade = ?, 
                main_subject = ?, hobby = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """,
            (
                data.get("nickname", ""),
                data.get("age"),
                data.get("school", ""),
                data.get("grade", ""),
                data.get("main_subject", "physics"),
                data.get("hobby", ""),
                user_id,
            ),
        )
    else:
        # Проверяем, есть ли колонка is_guest
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [column[1] for column in cursor.fetchall()]

        if "is_guest" in columns:
            cursor.execute(
                """
                INSERT INTO profiles (
                    user_id, username, nickname, age, school, 
                    grade, main_subject, hobby, is_guest
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    username,
                    data.get("nickname", ""),
                    data.get("age"),
                    data.get("school", ""),
                    data.get("grade", ""),
                    data.get("main_subject", "physics"),
                    data.get("hobby", ""),
                    data.get("is_guest", 0),
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO profiles (
                    user_id, username, nickname, age, school, 
                    grade, main_subject, hobby
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    username,
                    data.get("nickname", ""),
                    data.get("age"),
                    data.get("school", ""),
                    data.get("grade", ""),
                    data.get("main_subject", "physics"),
                    data.get("hobby", ""),
                ),
            )

    conn.commit()
    conn.close()
    return True


def save_guest_profile(user_id, username, data):
    """Сохранение гостевого профиля"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, есть ли колонка is_guest
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [column[1] for column in cursor.fetchall()]

    if "is_guest" in columns:
        cursor.execute(
            """
            INSERT INTO profiles (
                user_id, username, nickname, age, school, 
                grade, main_subject, hobby, is_guest
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                username,
                data.get("nickname", ""),
                data.get("age"),
                data.get("school", ""),
                data.get("grade", ""),
                data.get("main_subject", "physics"),
                data.get("hobby", ""),
                1,  # is_guest = True
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO profiles (
                user_id, username, nickname, age, school, 
                grade, main_subject, hobby
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                username,
                data.get("nickname", ""),
                data.get("age"),
                data.get("school", ""),
                data.get("grade", ""),
                data.get("main_subject", "physics"),
                data.get("hobby", ""),
            ),
        )

    conn.commit()
    conn.close()
    return True


def get_profile(user_id):
    """Получение профиля пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, есть ли колонка is_guest
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [column[1] for column in cursor.fetchall()]

    if "is_guest" in columns:
        cursor.execute(
            """
            SELECT username, nickname, age, school, grade, main_subject, hobby, is_guest
            FROM profiles WHERE user_id = ?
        """,
            (user_id,),
        )
    else:
        cursor.execute(
            """
            SELECT username, nickname, age, school, grade, main_subject, hobby, 0 as is_guest
            FROM profiles WHERE user_id = ?
        """,
            (user_id,),
        )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "username": row[0],
            "nickname": row[1] or "",
            "age": row[2],
            "school": row[3] or "",
            "grade": row[4] or "",
            "main_subject": row[5] or "physics",
            "hobby": row[6] or "",
            "is_guest": row[7] == 1 if len(row) > 7 else False,
        }
    return None


def get_all_profiles():
    """Получение всех профилей (для админа)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, есть ли колонка is_guest
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [column[1] for column in cursor.fetchall()]

    if "is_guest" in columns:
        cursor.execute("""
            SELECT id, username, nickname, age, school, grade, main_subject, 
                   created_at, is_guest 
            FROM profiles ORDER BY created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, username, nickname, age, school, grade, main_subject, 
                   created_at, 0 as is_guest 
            FROM profiles ORDER BY created_at DESC
        """)

    profiles = cursor.fetchall()
    conn.close()
    return profiles
