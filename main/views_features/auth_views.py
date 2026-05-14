from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models_features.profile_feature import get_profile, save_profile
from main.models_features.settings_feature import get_user_settings, update_user_settings
from main.models_features.question_feature import get_recent_questions
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer
from .helpers import get_menu


def index(request):
    # ПРОСТАЯ ПРОВЕРКА БАНА
    if request.user.is_authenticated:
        try:
            import subprocess
            result = subprocess.run(['python', 'check_ban.py', str(request.user.id)], capture_output=True, text=True)

            if result.stdout.strip() == 'banned':
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT ban_reason, banned_at, banned_until FROM main_profile WHERE user_id = %s",
                                   [request.user.id])
                    row = cursor.fetchone()
                    return render(request, 'banned.html', {
                        'ban_reason': row[0],
                        'banned_at': row[1],
                        'banned_until': row[2],
                    })
        except Exception as e:
            print(f"Error: {e}")

    questions = get_recent_questions(10)

    # ПОЛУЧАЕМ ДАННЫЕ ПРОФИЛЯ ДЛЯ ГЛАВНОЙ СТРАНИЦЫ
    profile_data = None
    questions_count = 0
    answers_count = 0
    ratings_received = 0

    if request.user.is_authenticated:
        try:
            profile_data = get_profile(request.user.id)
            questions_count = Question.objects.filter(user=request.user).count()
            answers_count = Answer.objects.filter(user=request.user).count()
            # ratings_received - если есть такая логика, оставь 0 или добавь
        except:
            pass

    return render(request, 'index.html', {
        'questions': questions,
        'menu': get_menu(request),
        'user': request.user,
        'profile': profile_data,
        'questions_count': questions_count,
        'answers_count': answers_count,
        'ratings_received': ratings_received,
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'register.html', {'error': 'Пароли не совпадают'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Пользователь уже существует'})

        user = User.objects.create_user(username=username, email=email, password=password)

        save_profile(user.id, username, {
            'nickname': username,
            'age': None,
            'hobby': '',
            'main_subject': 'general',
            'role': 'user'
        })

        login(request, user)
        return redirect('/')

    return render(request, 'register.html', {'menu': get_menu(request)})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})

    return render(request, 'login.html', {'menu': get_menu(request)})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile(request, username):
    profile_user = User.objects.get(username=username)
    questions_count = profile_user.questions.count()
    answers_count = profile_user.answers.count()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'questions_count': questions_count,
        'answers_count': answers_count,
        'menu': get_menu(request),
        'user': request.user
    })


@login_required
def settings(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        age = request.POST.get('age')
        hobby = request.POST.get('hobby')
        main_subject = request.POST.get('main_subject')

        # Обработка пустого возраста
        if age == '':
            age = None
        else:
            try:
                age = int(age)
            except ValueError:
                age = None

        save_profile(request.user.id, request.user.username, {
            'nickname': nickname,
            'age': age,
            'hobby': hobby,
            'main_subject': main_subject,
        })

        update_user_settings(request.user.id, {
            'notifications': request.POST.get('notifications') == 'on',
            'theme': request.POST.get('theme', 'light'),
            'language': request.POST.get('language', 'ru'),
        })

        # ПОСЛЕ СОХРАНЕНИЯ - ПОЛУЧАЕМ ОБНОВЛЁННЫЕ ДАННЫЕ
        profile_data = get_profile(request.user.id)
        settings_data = get_user_settings(request.user.id)

        return render(request, 'settings.html', {
            'profile': profile_data,
            'settings': settings_data,
            'saved': True,
            'menu': get_menu(request),
            'user': request.user
        })

    profile_data = get_profile(request.user.id)
    settings_data = get_user_settings(request.user.id)

    return render(request, 'settings.html', {
        'profile': profile_data,
        'settings': settings_data,
        'menu': get_menu(request),
        'user': request.user
    })