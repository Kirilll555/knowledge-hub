import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.models_features.answer_rating_feature import Answer
from django.db.models import Count, Q
from main.models_features import (
    create_question, get_question_by_id, create_answer, get_answers_for_question,
    rate_answer, add_activity, Question,
)
from .helpers import get_menu


def ask_question(request):
    """ Страница создания вопроса """

    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        subject = request.POST.get('subject', 'general')

        if title and content:
            question_id = create_question(request.user.id, title, content, subject)
            add_activity(request.user.id, 'ask_question', question_id=question_id)
            return redirect(f'/question/{question_id}/')
        else:
            return render(request, 'ask.html', {'error': 'Заполните все поля', 'menu': get_menu(request)})

    return render(request, 'ask.html', {'menu': get_menu(request)})


def question_detail(request, question_id):
    """ Страница вопроса и ответов """

    question = get_question_by_id(question_id)
    if not question:
        return render(request, '404.html', {'menu': get_menu(request)}, status=404)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/login/?next=/question/{}/'.format(question_id))

        content = request.POST.get('content', '').strip()
        if content:
            create_answer(request.user.id, question_id, content)
            add_activity(request.user.id, 'answer_question', question_id=question_id)
            return redirect(f'/question/{question_id}/')

    answers = get_answers_for_question(
        question_id,
        request.user.id if request.user.is_authenticated else None
    )

    return render(request, 'question.html', {
        'question': question,
        'answers': answers,
        'menu': get_menu(request),
        'user': request.user
    })


@login_required
@csrf_exempt
def add_answer(request, question_id):
    """ Добавление ответа """

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            answer_id = create_answer(request.user.id, question_id, content)
            add_activity(request.user.id, 'answer_question', question_id=question_id)
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
def rate_answer_view(request, answer_id):
    """ Оценка ответа """

    if request.method == 'POST':
        data = json.loads(request.body)
        rating = data.get('rating')
        rating_value = 1 if rating == 'like' else 0
        rate_answer(request.user.id, answer_id, rating_value)

        answer = Answer.objects.get(id=answer_id)
        likes = answer.ratings.filter(is_like=True).count()
        dislikes = answer.ratings.filter(is_like=False).count()

        add_activity(request.user.id, 'like_answer' if rating == 'like' else 'dislike_answer', answer_id=answer_id)

        return JsonResponse({
            'success': True,
            'likes': likes,
            'dislikes': dislikes
        })
    return JsonResponse({'success': False})
