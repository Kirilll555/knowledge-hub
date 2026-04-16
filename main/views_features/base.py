from django.shortcuts import render, redirect
from datetime import datetime
from main.utils.AI.Assistant import Assistant

from main.models import IVAN_DATA

def settings(request):
    context = {
        'user_data': IVAN_DATA,
    }
    return render(request, 'settings.html', context)

def get_menu():
    return [
        {'name': 'Главная', 'url': '/'},
    ]


def question_detail(request):
    return render(request, 'question.html')

def index(request):
    return render(request, 'index.html')


def profile(request):
    return render(request, 'profile.html')


def questions(request):
    return render(request, 'questions.html')


def ask_ai(request):
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

    return render(request, 'ask_ai.html', {
        'answer': answer,
        'error': error,
        'question': question
    })

def ask_question(request):
    return render(request, 'ask.html')