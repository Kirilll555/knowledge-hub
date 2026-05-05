import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.models_features.chat_feature import (
    ChatSession, get_user_sessions, get_session_messages,
    save_message, update_session_title, delete_session
)
from main.utils.ai_client import AIClient
from .helpers import get_menu


def search_question(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        session_id = data.get('session_id')

        result = AIClient().generate(question)

        if result.get('success') and session_id:
            save_message(session_id, 'assistant', result.get('answer'))

        return JsonResponse(result)

    question = request.GET.get('q', '')
    session_id = None
    if question and request.user.is_authenticated:
        session = ChatSession.objects.create(user_id=request.user.id, title=question[:50])
        session_id = session.id
        save_message(session.id, 'user', question)

    return render(request, 'search_question.html', {
        'question': question,
        'session_id': session_id,
        'menu': get_menu(request),
        'user': request.user
    })


@csrf_exempt
def regenerate_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        session_id = data.get('session_id')
        old_answer = data.get('old_answer', '')

        result = AIClient().regenerate(question, old_answer)

        if result.get('success') and session_id:
            from main.models_features.chat_feature import ChatMessage
            ChatMessage.objects.filter(session_id=session_id, role='assistant').delete()
            save_message(session_id, 'assistant', result['answer'])

        return JsonResponse(result)
    return JsonResponse({'error': 'method'})


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

        full_question = f"{context}\nПользователь: {question}\nАссистент:" if context else question
        result = AIClient().generate(full_question)

        if result.get('success'):
            answer = result['answer']
            save_message(current_session.id, 'assistant', answer)
            if messages.count() == 0:
                update_session_title(current_session.id, None)
            return JsonResponse({'success': True, 'answer': answer})

        return JsonResponse({'success': False, 'error': result.get('error')})

    return render(request, 'ask_ai.html', {
        'current_session': current_session,
        'sessions': sessions,
        'messages': messages,
        'menu': get_menu(request),
        'user': request.user
    })


@csrf_exempt
def create_ai_session(request):
    if request.method == 'POST':
        session = ChatSession.objects.create(user_id=request.user.id, title='Новый диалог')
        return JsonResponse({'success': True, 'session_id': session.id})
    return JsonResponse({'success': False})


@csrf_exempt
def delete_ai_session(request, session_id):
    if request.method == 'POST':
        delete_session(session_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def rename_ai_session(request, session_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_title = data.get('title', '').strip()
        if new_title:
            ChatSession.objects.filter(id=session_id, user_id=request.user.id).update(title=new_title)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})