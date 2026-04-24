from datetime import datetime
from django.shortcuts import render
from main.models_features import get_recent_questions, get_profile
from main.models_features import AnswerRating
from .helpers import get_menu


def index(request):
    """ Главная страница """

    today = datetime.now().strftime('%d.%m.%Y')
    recent_questions = get_recent_questions(limit=10)

    profile = None
    questions_count = 0
    answers_count = 0
    ratings_received = 0

    if request.user.is_authenticated:
        profile = get_profile(request.user.id)
        questions_count = request.user.questions.filter(is_deleted=False).count()
        answers_count = request.user.answers.filter(is_deleted=False).count()
        ratings_received = AnswerRating.objects.filter(answer__user=request.user).count()

    return render(request, 'index.html', {
        'today_date': today,
        'page_title': 'Knowledge Hub - Главная',
        'questions': recent_questions,
        'menu': get_menu(request),
        'user': request.user,
        'profile': profile,
        'questions_count': questions_count,
        'answers_count': answers_count,
        'ratings_received': ratings_received
    })
