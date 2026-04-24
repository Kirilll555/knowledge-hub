from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from main.models_features import (
    get_all_complaints, resolve_complaint, get_moderation_logs,
    delete_question_moderate, delete_answer_moderate,
    ban_user, unban_user, set_moderator, remove_moderator,
    check_admin_access
)
from .helpers import get_menu, moderator_required, admin_required


@login_required
@moderator_required
def moderation_panel(request):
    """ Панель модерации """

    complaints = get_all_complaints(resolved=False)
    resolved_complaints = get_all_complaints(resolved=True)
    logs = get_moderation_logs(50)

    users = User.objects.select_related('profile').all() if check_admin_access(request.user) else []

    return render(request, 'moderation.html', {
        'complaints': complaints,
        'resolved_complaints': resolved_complaints,
        'logs': logs,
        'users': users,
        'is_admin': check_admin_access(request.user),
        'menu': get_menu(request),
        'user': request.user
    })


@login_required
@moderator_required
@csrf_exempt
def moderate_resolve_complaint(request, complaint_id):
    """ Решение жалобы """

    if request.method == 'POST':
        resolve_complaint(complaint_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@moderator_required
@csrf_exempt
def moderate_delete_question(request):
    """ Удаление вопроса модератором """

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        reason = request.POST.get('reason', '')
        delete_question_moderate(question_id, request.user.id, reason)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@moderator_required
@csrf_exempt
def moderate_delete_answer(request):
    """ Удаление ответа модератором """

    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        reason = request.POST.get('reason', '')
        delete_answer_moderate(answer_id, request.user.id, reason)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@moderator_required
@csrf_exempt
def moderate_ban_user(request):
    """ Блокировка пользователя модератором """

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        reason = request.POST.get('reason', '')
        ban_user(user_id, request.user.id, reason)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@moderator_required
@csrf_exempt
def moderate_unban_user(request):
    """ Разблокировка пользователя """

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        unban_user(user_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@admin_required
@csrf_exempt
def moderate_set_moderator(request):
    """ Назначение модератора """

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        set_moderator(user_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@admin_required
@csrf_exempt
def moderate_remove_moderator(request):
    """ Снятие модератора """

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        remove_moderator(user_id, request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
