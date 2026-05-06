from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models_features.profile_feature import get_profile, save_profile
from main.models_features.settings_feature import get_user_settings, update_user_settings
from main.models_features.question_feature import get_recent_questions
from .helpers import get_menu


def index(request):
    questions = get_recent_questions(10)
    return render(request, 'index.html', {
        'questions': questions,
        'menu': get_menu(request),
        'user': request.user
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
        
        return render(request, 'settings.html', {'saved': True, 'menu': get_menu(request)})
    
    profile_data = get_profile(request.user.id)
    settings_data = get_user_settings(request.user.id)
    
    return render(request, 'settings.html', {
        'profile': profile_data,
        'settings': settings_data,
        'menu': get_menu(request),
        'user': request.user
    })
