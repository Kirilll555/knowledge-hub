import sqlite3
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import datetime
from main.utils.AI.Assistant import Assistant
from main import database


def settings(request):
    """Страница настроек пользователя"""
    if not request.user.is_authenticated:
        return render(request, 'settings.html', {'user': request.user})

    settings_data = database.get_user_settings(request.user.id)
    profile_data = database.get_profile(request.user.id)

    if request.method == 'POST':
        # Обновляем настройки
        new_settings = {
            'theme': request.POST.get('theme', 'light'),
            'notifications': request.POST.get('notifications') == 'on',
            'language': request.POST.get('language', 'ru'),
        }
        database.update_user_settings(request.user.id, new_settings)

        # Обновляем профиль
        profile_update = {
            'nickname': request.POST.get('nickname', ''),
            'age': request.POST.get('age'),
            'school': request.POST.get('school', ''),
            'grade': request.POST.get('grade', ''),
            'main_subject': request.POST.get('main_subject', 'physics'),
            'hobby': request.POST.get('hobby', ''),
        }
        database.save_profile(request.user.id, request.user.username, profile_update)

        # Обновляем email пользователя
        email = request.POST.get('email', '')
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()

        return redirect('/settings/?saved=1')

    return render(request, 'settings.html', {
        'settings': settings_data,
        'profile': profile_data,
        'user': request.user,
        'saved': request.GET.get('saved')
    })

def get_menu(request):
    """Динамическое меню"""
    menu = [
        {"name": "Главная", "url": "/"},
        {"name": "Задать вопрос", "url": "/ask/"},
        {"name": "Спросить ИИ", "url": "/search_question/"},
    ]

    if request.user.is_authenticated:
        menu.append({"name": request.user.username, "url": f"/profile/{request.user.username}/"})
        menu.append({"name": "Настройки", "url": "/settings/"})
        menu.append({"name": "Выйти", "url": "/logout/"})
    else:
        menu.append({"name": "Войти", "url": "/login/"})
        menu.append({"name": "Регистрация", "url": "/register/"})

    return menu

def question_detail(request, question_id):
    question = database.get_question_by_id(question_id)
    if not question:
        return render(request, '404.html', {'menu': get_menu(request)}, status=404)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/login/?next=/question/{}/'.format(question_id))

        content = request.POST.get('content', '').strip()
        if content:
            database.create_answer(request.user.id, question_id, content)
            return redirect(f'/question/{question_id}/')

    answers = database.get_answers_for_question(
        question_id,
        request.user.id if request.user.is_authenticated else None
    )

    return render(request, 'question.html', {
        'question': question,
        'answers': answers,
        'menu': get_menu(request),
        'user': request.user
    })


def index(request):
    today = datetime.now().strftime('%d.%m.%Y')
    recent_questions = database.get_recent_questions(limit=10)

    # Данные для авторизованного пользователя
    profile = None
    questions_count = 0
    answers_count = 0
    ratings_received = 0

    if request.user.is_authenticated:
        profile = database.get_profile(request.user.id)
        print("Profile data:", profile)  # Для отладки - посмотри в терминале

        conn = sqlite3.connect(database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions WHERE user_id = ? AND is_deleted = 0", (request.user.id,))
        questions_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM answers WHERE user_id = ? AND is_deleted = 0", (request.user.id,))
        answers_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM answer_ratings ar
            JOIN answers a ON ar.answer_id = a.id
            WHERE a.user_id = ?
        """, (request.user.id,))
        ratings_received = cursor.fetchone()[0]
        conn.close()

    context = {
        'today_date': today,
        'page_title': 'Промышленное программирование - Занятие 12',
        'questions': recent_questions,
        'menu': get_menu(request),
        'user': request.user,
        'profile': profile,  # <-- ВАЖНО: передаём как 'profile'
        'questions_count': questions_count,
        'answers_count': answers_count,
        'ratings_received': ratings_received
    }
    return render(request, 'index.html', context)


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, '404.html', {'menu': get_menu(request)}, status=404)

    profile_data = database.get_profile(user.id)
    activities = database.get_user_activities(user.id, limit=50)

    return render(request, 'profile.html', {
        'profile_user': user,
        'profile_data': profile_data,
        'activities': activities,
        'menu': get_menu(request),
        'current_user': request.user
    })


def questions(request):
    return render(request, 'questions.html', {'menu': get_menu(request)})


def search_question(request):
    answer = None
    error = None
    question = None

    if request.method == 'GET':
        question = request.GET.get('q', '')
    elif request.method == 'POST':
        question = request.POST.get('question', '')

    if question:
        assistant = Assistant()
        result = assistant.ask(question)
        if result.get('success'):
            answer = result.get('answer')
        else:
            error = result.get('error', 'Ошибка при получении ответа')

    return render(request, 'search_question.html', {
        'answer': answer,
        'error': error,
        'question': question,
        'menu': get_menu(request),
        'user': request.user
    })


# ========== НОВЫЕ ФУНКЦИИ ДЛЯ АУТЕНТИФИКАЦИИ ==========

def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # Проверки
        if not username or not password:
            return render(request, 'register.html', {'error': 'Заполните все обязательные поля'})

        if password != password2:
            return render(request, 'register.html',
                          {'error': 'Пароли не совпадают', 'username': username, 'email': email})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html',
                          {'error': 'Пользователь с таким именем уже существует', 'email': email})

        # Создаем пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Создаем профиль в БД
        database.save_profile(user.id, username, {
            'nickname': username,
            'is_guest': False
        })

        # Автоматически входим
        auth_login(request, user)
        return redirect('/')

    return render(request, 'register.html', {'menu': get_menu(request)})


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            return render(request, 'login.html',
                          {'error': 'Неверное имя пользователя или пароль', 'menu': get_menu(request)})

    return render(request, 'login.html', {'menu': get_menu(request)})


def logout_view(request):
    """Выход из системы"""
    auth_logout(request)
    return redirect('/')


def ask_question(request):
    """Страница создания вопроса"""
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        subject = request.POST.get('subject', 'general')

        if title and content:
            question_id = database.create_question(request.user.id, title, content, subject)
            return redirect(f'/question/{question_id}/')
        else:
            return render(request, 'ask.html', {'error': 'Заполните все поля', 'menu': get_menu(request)})

    return render(request, 'ask.html', {'menu': get_menu(request)})


@login_required
@csrf_exempt
def add_answer(request, question_id):
    """AJAX добавление ответа"""
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            answer_id = database.create_answer(request.user.id, question_id, content)
            return JsonResponse({
                'success': True,
                'answer_id': answer_id,
                'author': request.user.username,
                'content': content,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
    return JsonResponse({'success': False, 'error': 'Пустой ответ'})


@login_required
@csrf_exempt
def rate_answer(request, answer_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        rating = data.get('rating')
        rating_value = 1 if rating == 'like' else 0
        action = database.rate_answer(request.user.id, answer_id, rating_value)

        conn = sqlite3.connect(database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN rating = 1 THEN 1 END) as likes,
                COUNT(CASE WHEN rating = 0 THEN 1 END) as dislikes
            FROM answer_ratings WHERE answer_id = ?
        """, (answer_id,))
        likes, dislikes = cursor.fetchone()
        conn.close()

        return JsonResponse({
            'success': True,
            'action': action,
            'likes': likes,
            'dislikes': dislikes
        })
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
def submit_complaint(request):
    """Отправка жалобы"""
    if request.method == 'POST':
        complaint_type = request.POST.get('type')
        reason = request.POST.get('reason', '').strip()
        question_id = request.POST.get('question_id')
        answer_id = request.POST.get('answer_id')

        if not reason:
            return JsonResponse({'success': False, 'error': 'Укажите причину жалобы'})

        if complaint_type == 'question' and question_id:
            database.create_complaint(request.user.id, 'question', reason, question_id=question_id)
        elif complaint_type == 'answer' and answer_id:
            database.create_complaint(request.user.id, 'answer', reason, answer_id=answer_id)
        else:
            return JsonResponse({'success': False, 'error': 'Неверные данные'})

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
def moderation_panel(request):
    """Панель модерации"""
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Доступ запрещен")

    complaints = database.get_all_complaints(resolved=False)
    resolved_complaints = database.get_all_complaints(resolved=True)

    return render(request, 'moderation.html', {
        'complaints': complaints,
        'resolved_complaints': resolved_complaints[:20],
        'menu': get_menu(request)
    })


@login_required
@csrf_exempt
def resolve_complaint(request, complaint_id):
    """Отметить жалобу как решенную"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Нет прав'})

    database.resolve_complaint(complaint_id, request.user.id)
    return JsonResponse({'success': True})