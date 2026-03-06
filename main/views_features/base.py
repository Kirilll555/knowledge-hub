from django.shortcuts import render, redirect
from datetime import datetime
from main.utils.AI.Assistant import Assistant

def get_menu():
    return [
        {'name': 'Главная', 'url': '/'},
    ]

def home(request):
    context = {
        'user': request.user,
    }
    return render(request, '###home.html', context)

def about(request):
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

def questions(request):
    return render(request, 'questions.html')


def ask_ai(request):
    answer = None
    error = None

    if request.method == 'POST':
        question = request.POST.get('question', '')
        if question:
            assistant = Assistant()
            result = assistant.ask(question)
            if result.get('success'):
                answer = result.get('answer')
            else:
                error = result.get('error', 'Ошибка при получении ответа')

    return render(request, 'ask_ai.html', {
        'answer': answer,
        'error': error
    })

def ask_question(request):
    return render(request, 'ask.html')

def comments(request):
    return render(request, 'comments.html')

def settings(request):
    return render(request, 'settings.html')