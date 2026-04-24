from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render
from main.models_features import check_moderator_access, check_admin_access, check_user_access


def get_menu(request):
    """ Меню """

    menu = [
        {"name": "Главная", "url": "/"},
        {"name": "Задать вопрос", "url": "/ask/"},
        {"name": "Спросить ИИ", "url": "/search_question/"},
    ]

    if request.user.is_authenticated:
        menu.append({"name": request.user.username, "url": f"/profile/{request.user.username}/"})
        menu.append({"name": "Настройки", "url": "/settings/"})
        if check_moderator_access(request.user):
            menu.append({"name": "Модерация", "url": "/moderation/"})
        menu.append({"name": "Выйти", "url": "/logout/"})
    else:
        menu.append({"name": "Войти", "url": "/login/"})
        menu.append({"name": "Регистрация", "url": "/register/"})

    return menu


def moderator_required(view_func):
    """ Декоратор: доступ только для модераторов и админов """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not check_moderator_access(request.user):
            return HttpResponseForbidden("Доступ запрещён. Требуются права модератора.")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    """ Декоратор: доступ только для админов """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not check_admin_access(request.user):
            return HttpResponseForbidden("Доступ запрещён. Требуются права администратора.")
        return view_func(request, *args, **kwargs)

    return wrapper


def check_ban(view_func):
    """ Декоратор: проверка блокировки пользователя """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not check_user_access(request.user):
            return render(request, 'error.html', {'error': 'Ваш аккаунт заблокирован. Обратитесь к администратору.'})
        return view_func(request, *args, **kwargs)

    return wrapper
