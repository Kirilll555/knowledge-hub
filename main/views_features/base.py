from django.shortcuts import render, redirect
from datetime import datetime
from django.shortcuts import render



def get_menu():
    return [
        {'name': 'Главная', 'url': '/'},
    ]


def home(request):
    """Главная страница"""
    context = {
        'user': request.user,
    }
    return render(request, '###home.html', context)


def about(request):
    """Страница О нас"""
    return render(request, 'about.html')


def index(request):
    today = datetime.now().strftime('%d.%m.%Y')
    context = {
        'today_date': today,
        'page_title': 'Промышленное программирование - Занятие 12',
        'menu': get_menu(),
    }
    return render(request, 'index.html', context)

def register(request):
    return render(request, 'register.html')

def profile(request):
    return render(request, 'profile.html')
def login(request):
    return render(request, 'login.html')
