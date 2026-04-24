from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.models_features.chat_feature import (
    ChatSession, get_user_sessions, get_session_messages,
    save_message, update_session_title, delete_session
)
from main.utils.AI.assistant import Assistant
from main.utils.logger import log_ai, log_error
from .helpers import get_menu
import json


def search_question(request):
    answer = None
    error = None
    question = None

    if request.method == 'GET':
        question = request.GET.get('q', '')
    elif request.method == 'POST':
        question = request.POST.get('question', '')

    if question:
        try:
            assistant = Assistant()
            result = assistant.ask(question)
            if result.get('success'):
                answer = result.get('answer')
                log_ai(request.user, question, answer, success=True)
            else:
                error = result.get('error', 'Ошибка при получении ответа')
                log_ai(request.user, question, '', success=False, error=error)
        except Exception as e:
            error = str(e)
            log_error(e, 'search_question', request.user)

    return render(request, 'search_question.html', {
        'answer': answer,
        'error': error,
        'question': question,
        'menu': get_menu(request),
        'user': request.user
    })


@login_required
def ask_ai(request, session_id=None):
    sessions = get_user_sessions(request.user.id)

    current_session = None
    if session_id:
        for s in sessions:
            if s.id == session_id:
                current_session = s
                break

    if not current_session:
        if sessions.exists():
            current_session = sessions.first()
        else:
            current_session = ChatSession.objects.create(
                user_id=request.user.id,
                title='Новый диалог'
            )

    messages = get_session_messages(current_session.id)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()

        if not question:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Пустой вопрос'})
            return redirect('ask_ai', session_id=current_session.id)

        save_message(current_session.id, 'user', question)

        context = ""
        recent_messages = get_session_messages(current_session.id)[:10]
        for msg in recent_messages:
            if msg.role == 'user':
                context += f"Пользователь: {msg.content}\n"
            else:
                context += f"Ассистент: {msg.content}\n"

        assistant = Assistant()
        full_question = f"{context}\nПользователь: {question}\nАссистент:" if context else question
        result = assistant.ask(full_question)

        if result.get('success'):
            answer = result['answer']
            save_message(current_session.id, 'assistant', answer)
            log_ai(request.user, question, answer, success=True)
            if messages.count() == 0:
                update_session_title(current_session.id, None)
        else:
            answer = result.get('error', 'Ошибка генерации')
            log_ai(request.user, question, '', success=False, error=answer)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': result.get('success', False),
                'answer': answer
            })

        return redirect('ask_ai', session_id=current_session.id)

    return render(request, 'ask_ai.html', {
        'current_session': current_session,
        'sessions': sessions,
        'messages': messages,
        'menu': get_menu(request),
        'user': request.user
    })


@login_required
@csrf_exempt
def create_ai_session(request):
    if request.method == 'POST':
        session = ChatSession.objects.create(user_id=request.user.id, title='Новый диалог')
        return JsonResponse({'success': True, 'session_id': session.id})
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
def delete_ai_session(request, session_id):
    if request.method == 'POST':
        delete_session(session_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
def rename_ai_session(request, session_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_title = data.get('title', '').strip()
            if new_title:
                ChatSession.objects.filter(id=session_id, user_id=request.user.id).update(title=new_title)
                return JsonResponse({'success': True})
        except Exception:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})
