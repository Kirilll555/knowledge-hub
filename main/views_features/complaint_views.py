from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from main.models_features.complaint_feature import create_complaint
from main.models_features.complaint_feature import Complaint
from main.models_features.notification_feature import create_notification
from django.contrib.auth.models import User
import json


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_complaint_api(request):
    """API для создания жалобы"""
    try:
        data = json.loads(request.body)
        target_type = data.get('target_type')  # 'question', 'answer', 'user'
        target_id = data.get('target_id')
        complaint_type = data.get('complaint_type')
        description = data.get('description', '')
        reason = data.get('reason', complaint_type)
        
        # Создаем жалобу в зависимости от типа
        if target_type == 'question':
            complaint = create_complaint(
                user_id=request.user.id,
                target_type='question',
                complaint_type=complaint_type,
                reason=reason,
                description=description,
                question_id=target_id
            )
            target_info = f"Вопрос #{target_id}"
            
        elif target_type == 'answer':
            complaint = create_complaint(
                user_id=request.user.id,
                target_type='answer',
                complaint_type=complaint_type,
                reason=reason,
                description=description,
                answer_id=target_id
            )
            target_info = f"Ответ #{target_id}"
            
        else:  # user
            complaint = create_complaint(
                user_id=request.user.id,
                target_type='user',
                complaint_type=complaint_type,
                reason=reason,
                description=description,
                target_user_id=target_id
            )
            target_user = User.objects.get(id=target_id)
            target_info = f"Пользователя {target_user.username}"
        
        # Отправляем уведомление админам
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            complaint_text = dict(Complaint.COMPLAINT_TYPES).get(complaint_type, complaint_type)
            create_notification(
                user_id=admin.id,
                notification_type='system',
                title=f'🚩 Новая жалоба от {request.user.username}',
                message=f'Тип: {complaint_text}\nЦель: {target_info}\nОписание: {description[:100]}',
                link='/moderation/complaints/'
            )
        
        return JsonResponse({'success': True, 'complaint_id': complaint.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def submit_complaint(request):
    """Старая вьюха для совместимости"""
    return JsonResponse({'error': 'Use POST to /api/complaints/create/'}, status=405)
