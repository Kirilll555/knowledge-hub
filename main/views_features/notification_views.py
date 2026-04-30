from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from main.models_features.notification_feature import (
    get_user_notifications, 
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_count
)


@login_required
def get_notifications(request):
    """Возвращает список уведомлений пользователя"""
    notifications = get_user_notifications(request.user.id, limit=20)
    unread_count = get_unread_count(request.user.id)
    
    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'link': n.link,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d.%m.%Y %H:%M')
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)


@login_required
@csrf_exempt
def mark_read(request, notification_id):
    """Отмечает уведомление как прочитанное"""
    if request.method == 'POST':
        mark_notification_as_read(notification_id)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def mark_all_read(request):
    """Отмечает все уведомления как прочитанные"""
    if request.method == 'POST':
        mark_all_notifications_as_read(request.user.id)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
