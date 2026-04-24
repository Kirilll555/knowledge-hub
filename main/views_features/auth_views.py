from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from main.models_features import save_profile
from main.utils.logger import log_auth
from .helpers import get_menu


def register(request):
    """ Регистрация пользователя """

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            log_auth(username, 'register', success=False)
            return render(request, 'register.html', {
                'error': 'Заполните все обязательные поля',
                'menu': get_menu(request)
            })

        if password != password2:
            log_auth(username, 'register', success=False)
            return render(request, 'register.html', {
                'error': 'Пароли не совпадают',
                'username': username,
                'email': email,
                'menu': get_menu(request)
            })

        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            log_auth(username, 'register', success=False)
            return render(request, 'register.html', {
                'error': 'Пользователь с таким именем уже существует',
                'email': email,
                'menu': get_menu(request)
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        save_profile(user.id, username, {'nickname': username, 'role': 'user'})

        if User.objects.count() == 1:
            from main.models_features.profile_feature import Profile
            profile = Profile.objects.get(user=user)
            profile.role = 'admin'
            profile.save()

        auth_login(request, user)
        log_auth(user, 'register', success=True)
        return redirect('/')

    return render(request, 'register.html', {'menu': get_menu(request)})


def login_view(request):
    """ Вход в систему """

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            log_auth(user, 'login', success=True)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            log_auth(username, 'login', success=False)
            return render(request, 'login.html', {
                'error': 'Неверное имя пользователя или пароль',
                'menu': get_menu(request)
            })

    return render(request, 'login.html', {'menu': get_menu(request)})


def logout_view(request):
    """ Выход из системы """

    if request.user.is_authenticated:
        log_auth(request.user, 'logout', success=True)
    auth_logout(request)
    return redirect('/')
