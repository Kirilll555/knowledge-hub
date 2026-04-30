from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from main.models_features.complaint_feature import get_all_complaints, update_complaint_status
from main.models_features.question_feature import delete_question
from main.models_features.answer_rating_feature import delete_answer
from main.models_features.profile_feature import ban_user, unban_user, set_moderator, remove_moderator
from main.models_features.notification_feature import create_notification
from main.models_features.complaint_feature import Complaint
import json


@login_required
def complaints_list(request):
    """Страница со списком жалоб"""
    if not request.user.is_superuser:
        return render(request, 'access_denied.html', {'error': 'Доступ запрещен'})
    
    complaints = get_all_complaints()
    return render(request, 'moderation/complaints.html', {'complaints': complaints})


@login_required
def resolve_complaint(request, complaint_id):
    """Обработка жалобы - при одобрении удаляет контент"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        complaint = get_object_or_404(Complaint, id=complaint_id)
        
        if action == 'approve':
            # При одобрении - удаляем контент
            if complaint.question:
                delete_question(complaint.question.id, request.user.id)
                message = f'Вопрос #{complaint.question.id} удален'
                
                # Уведомление автору вопроса
                create_notification(
                    user_id=complaint.question.user.id,
                    notification_type='system',
                    title='⚠️ Ваш вопрос удален',
                    message=f'Ваш вопрос был удален модератором по жалобе. Причина: {complaint.reason}',
                    link='/'
                )
                
            elif complaint.answer:
                delete_answer(complaint.answer.id, request.user.id)
                message = f'Ответ #{complaint.answer.id} удален'
                
                # Уведомление автору ответа
                create_notification(
                    user_id=complaint.answer.user.id,
                    notification_type='system',
                    title='⚠️ Ваш ответ удален',
                    message=f'Ваш ответ был удален модератором по жалобе. Причина: {complaint.reason}',
                    link=f'/question/{complaint.answer.question.id}/'
                )
            
            update_complaint_status(complaint_id, 'approved')
            
            # Уведомление автору жалобы
            create_notification(
                user_id=complaint.user.id,
                notification_type='system',
                title='✅ Жалоба одобрена',
                message=f'Ваша жалоба одобрена. Контент удален. Спасибо за помощь!',
                link='/'
            )
            
        else:  # reject
            update_complaint_status(complaint_id, 'rejected')
            message = 'Жалоба отклонена'
            
            # Уведомление автору жалобы
            create_notification(
                user_id=complaint.user.id,
                notification_type='system',
                title='❌ Жалоба отклонена',
                message=f'Ваша жалоба отклонена. Нарушений не обнаружено.',
                link='/'
            )
        
        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_panel(request):
    """Панель модерации"""
    if not request.user.is_superuser:
        return render(request, 'access_denied.html', {'error': 'Доступ запрещен'})
    
    complaints = get_all_complaints('pending')
    return render(request, 'moderation/panel.html', {'complaints': complaints})


@login_required
def moderate_resolve_complaint(request, complaint_id):
    """Решение жалобы (API)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        update_complaint_status(complaint_id, status)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_delete_question(request, question_id):
    """Удаление вопроса"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        delete_question(question_id, request.user.id)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_delete_answer(request, answer_id):
    """Удаление ответа"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        delete_answer(answer_id, request.user.id)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_ban_user(request, user_id):
    """Блокировка пользователя"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        reason = data.get('reason', 'Нарушение правил')
        ban_user(user_id, request.user.id, reason)
        
        # Уведомление заблокированному пользователю
        create_notification(
            user_id=user_id,
            notification_type='system',
            title='🔒 Вы заблокированы',
            message=f'Ваш аккаунт заблокирован модератором. Причина: {reason}',
            link='/'
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_unban_user(request, user_id):
    """Разблокировка пользователя"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        unban_user(user_id, request.user.id)
        
        # Уведомление разблокированному пользователю
        create_notification(
            user_id=user_id,
            notification_type='system',
            title='🔓 Вы разблокированы',
            message='Ваш аккаунт разблокирован модератором',
            link='/'
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_set_moderator(request, user_id):
    """Назначение модератором"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        set_moderator(user_id, request.user.id)
        
        # Уведомление новому модератору
        create_notification(
            user_id=user_id,
            notification_type='system',
            title='👮‍♂️ Вы назначены модератором',
            message='Поздравляем! Теперь вы можете модерировать контент на платформе',
            link='/moderation/'
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def moderate_remove_moderator(request, user_id):
    """Снятие модератора"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        remove_moderator(user_id, request.user.id)
        
        # Уведомление бывшему модератору
        create_notification(
            user_id=user_id,
            notification_type='system',
            title='👋 Права модератора сняты',
            message='Ваши права модератора были сняты',
            link='/'
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
