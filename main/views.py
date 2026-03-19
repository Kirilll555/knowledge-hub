from django.shortcuts import render, redirect
from datetime import datetime
from django.shortcuts import render


def get_menu():
    return [
        {"name": "Главная", "url": "/"},
    ]


def index(request):
    return render(request, "index.html")  # просто имя файла


def new_question(request):
    return render(request, "new_question.html")  # просто имя файла


def question_detail(request, question_id):
    return render(request, "question_detail.html", {"question_id": question_id})


def profile(request, username):
    return render(request, "profile.html", {"username": username})


def articles(request):
    return render(request, "articles.html")


def moderation(request):
    return render(request, "moderation.html")


def ratings(request):
    return render(request, "ratings.html")


def login_page(request):
    return render(request, "login.html")
