from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from main.models_features.complaint_feature import create_complaint, Complaint
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
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        complaint_type = data.get('complaint_type')
        description = data.get('description', '')
        
        # Создаем жалобу (без краткой причины)
        if target_type == 'question':
            complaint = create_complaint(
                user_id=request.user.id,
                complaint_type=complaint_type,
                reason=complaint_type,  # используем тип как причину
                description=description,
                question_id=target_id
            )
        else:  # answer
            complaint = create_complaint(
                user_id=request.user.id,
                complaint_type=complaint_type,
                reason=complaint_type,
                description=description,
                answer_id=target_id
            )
        
        # Отправляем уведомление админам
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            create_notification(
                user_id=admin.id,
                notification_type='system',
                title=f'🚩 Новая жалоба от {request.user.username}',
                message=f'Тип: {dict(Complaint.COMPLAINT_TYPES).get(complaint_type, complaint_type)}\nОписание: {description[:100]}',
                link='/admin/complaints/'
            )
        
        return JsonResponse({'success': True, 'complaint_id': complaint.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def submit_complaint():
    return None