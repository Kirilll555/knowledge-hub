import sqlite3
import os
from django.conf import settings
from django.core.checks import database
from django.shortcuts import render, redirect

DB_PATH = os.path.join(settings.BASE_DIR, "db.sqlite3")


# ========== ТАБЛИЦА ПРОФИЛЕЙ ==========

def init_profiles_table():
    """Создание таблицы profiles"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT NOT NULL,
            nickname TEXT,
            age INTEGER,
            school TEXT,
            grade TEXT,
            main_subject TEXT DEFAULT 'physics',
            hobby TEXT,
            is_guest INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Таблица profiles создана")


def save_profile(user_id, username, data):
    """Сохранение или обновление профиля"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE profiles 
            SET nickname = ?, age = ?, school = ?, grade = ?, 
                main_subject = ?, hobby = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (data.get("nickname", ""), data.get("age"), data.get("school", ""),
              data.get("grade", ""), data.get("main_subject", "physics"),
              data.get("hobby", ""), user_id))
    else:
        cursor.execute("""
            INSERT INTO profiles (user_id, username, nickname, age, school, 
            grade, main_subject, hobby, is_guest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, data.get("nickname", ""), data.get("age"),
              data.get("school", ""), data.get("grade", ""),
              data.get("main_subject", "physics"), data.get("hobby", ""),
              data.get("is_guest", 0)))

    conn.commit()
    conn.close()
    return True


def get_profile(user_id):
    """Получение профиля пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, nickname, age, school, grade, main_subject, hobby, is_guest
        FROM profiles WHERE user_id = ?
    """, (user_id,))
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


# Запускаем создание таблицы profiles
init_profiles_table()

def init_qa_tables():
    """Создание таблиц для вопросов, ответов, оценок и т.д."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица вопросов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            subject TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    # Таблица ответов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    # Таблица оценок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answer_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            answer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, answer_id)
        )
    """)

    # Таблица жалоб
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            complaint_type TEXT NOT NULL,
            question_id INTEGER,
            answer_id INTEGER,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0
        )
    """)

    # Таблица истории ИИ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица активности
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            question_id INTEGER,
            answer_id INTEGER,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица настроек
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            theme TEXT DEFAULT 'light',
            notifications INTEGER DEFAULT 1,
            language TEXT DEFAULT 'ru',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Таблицы для Q&A созданы")


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ВОПРОСАМИ ==========

def create_question(user_id, title, content, subject='general'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (user_id, title, content, subject)
        VALUES (?, ?, ?, ?)
    """, (user_id, title, content, subject))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


def get_recent_questions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.title, q.content, q.subject, q.created_at, 
               q.user_id, p.username, p.nickname,
               (SELECT COUNT(*) FROM answers WHERE question_id = q.id AND is_deleted = 0) as answers_count
        FROM questions q
        LEFT JOIN profiles p ON q.user_id = p.user_id
        WHERE q.is_deleted = 0
        ORDER BY q.created_at DESC
        LIMIT ?
    """, (limit,))

    questions = []
    for row in cursor.fetchall():
        questions.append({
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'subject': row[3],
            'created_at': row[4],
            'user_id': row[5],
            'author_name': row[7] or row[6],
            'answers_count': row[8]
        })
    conn.close()
    return questions


def get_question_by_id(question_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.title, q.content, q.subject, q.created_at, 
               q.user_id, p.username, p.nickname
        FROM questions q
        LEFT JOIN profiles p ON q.user_id = p.user_id
        WHERE q.id = ? AND q.is_deleted = 0
    """, (question_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'subject': row[3],
            'created_at': row[4],
            'user_id': row[5],
            'author_name': row[7] or row[6]
        }
    return None


def create_answer(user_id, question_id, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO answers (user_id, question_id, content)
        VALUES (?, ?, ?)
    """, (user_id, question_id, content))
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return answer_id


def get_answers_for_question(question_id, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.content, a.created_at, a.user_id,
               p.username, p.nickname
        FROM answers a
        LEFT JOIN profiles p ON a.user_id = p.user_id
        WHERE a.question_id = ? AND a.is_deleted = 0
        ORDER BY a.created_at ASC
    """, (question_id,))

    answers = []
    for row in cursor.fetchall():
        # Получаем оценки
        cursor.execute("""
            SELECT COUNT(CASE WHEN rating = 1 THEN 1 END) as likes,
                   COUNT(CASE WHEN rating = 0 THEN 1 END) as dislikes
            FROM answer_ratings WHERE answer_id = ?
        """, (row[0],))
        likes, dislikes = cursor.fetchone()

        answer = {
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'user_id': row[3],
            'author_name': row[5] or row[4],
            'likes': likes or 0,
            'dislikes': dislikes or 0,
            'user_rating': None
        }

        if user_id:
            cursor.execute("SELECT rating FROM answer_ratings WHERE user_id = ? AND answer_id = ?",
                           (user_id, answer['id']))
            rating_row = cursor.fetchone()
            if rating_row:
                answer['user_rating'] = 'like' if rating_row[0] == 1 else 'dislike'

        answers.append(answer)

    conn.close()
    return answers


def rate_answer(user_id, answer_id, rating):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, rating FROM answer_ratings WHERE user_id = ? AND answer_id = ?",
                   (user_id, answer_id))
    existing = cursor.fetchone()

    if existing:
        if existing[1] == rating:
            cursor.execute("DELETE FROM answer_ratings WHERE id = ?", (existing[0],))
        else:
            cursor.execute("UPDATE answer_ratings SET rating = ? WHERE id = ?", (rating, existing[0]))
    else:
        cursor.execute("INSERT INTO answer_ratings (user_id, answer_id, rating) VALUES (?, ?, ?)",
                       (user_id, answer_id, rating))

    conn.commit()
    conn.close()
    return True


# ========== ФУНКЦИИ ДЛЯ АКТИВНОСТИ ==========

def add_activity(user_id, activity_type, question_id=None, answer_id=None, metadata=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_activities (user_id, activity_type, question_id, answer_id, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, activity_type, question_id, answer_id, metadata))
    conn.commit()
    conn.close()


def get_user_activities(user_id, limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, activity_type, question_id, answer_id, metadata, created_at
        FROM user_activities
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))

    activities = []
    for row in cursor.fetchall():
        activity = {
            'id': row[0],
            'activity_type': row[1],
            'question_id': row[2],
            'answer_id': row[3],
            'metadata': row[4],
            'created_at': row[5]
        }

        if row[2]:
            conn2 = sqlite3.connect(DB_PATH)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT title FROM questions WHERE id = ?", (row[2],))
            q_row = cursor2.fetchone()
            if q_row:
                activity['question_title'] = q_row[0]
            conn2.close()

        activities.append(activity)

    conn.close()
    return activities


def get_user_settings(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT theme, notifications, language FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {'theme': row[0], 'notifications': bool(row[1]), 'language': row[2]}
    return {'theme': 'light', 'notifications': True, 'language': 'ru'}


def update_user_settings(user_id, settings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_settings (user_id, theme, notifications, language, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            theme = excluded.theme,
            notifications = excluded.notifications,
            language = excluded.language,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, settings.get('theme', 'light'),
          1 if settings.get('notifications', True) else 0,
          settings.get('language', 'ru')))
    conn.commit()
    conn.close()


def create_complaint(user_id, complaint_type, reason, question_id=None, answer_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (user_id, complaint_type, question_id, answer_id, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, complaint_type, question_id, answer_id, reason))
    conn.commit()
    conn.close()


def get_all_complaints(resolved=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, complaint_type, question_id, answer_id, reason, created_at, is_resolved
        FROM complaints WHERE is_resolved = ?
        ORDER BY created_at DESC
    """, (1 if resolved else 0,))
    complaints = cursor.fetchall()
    conn.close()
    return complaints


def resolve_complaint(complaint_id, resolved_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET is_resolved = 1 WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()


def delete_question(question_id, moderator_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE questions SET is_deleted = 1 WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


def delete_answer(answer_id, moderator_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE answers SET is_deleted = 1 WHERE id = ?", (answer_id,))
    conn.commit()
    conn.close()


def save_ai_chat(user_id, question, answer):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_chat_history (user_id, question, answer)
        VALUES (?, ?, ?)
    """, (user_id, question, answer))
    conn.commit()
    conn.close()

# Запускаем создание таблиц
init_qa_tables()