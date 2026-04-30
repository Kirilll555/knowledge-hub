from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('answer', 'Ответ на вопрос'),
        ('rating', 'Оценка ответа'),
        ('system', 'Системное уведомление'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


def create_notification(user_id, notification_type, title, message, link='', max_per_user=100):
    """Создает уведомление с ограничением max_per_user штук"""

    # Удаляем самые старые уведомления если превышен лимит
    count = Notification.objects.filter(user_id=user_id).count()
    if count >= max_per_user:
        to_delete = count - max_per_user + 1
        oldest_notifications = Notification.objects.filter(user_id=user_id).order_by('created_at')[:to_delete]
        for notif in oldest_notifications:
            notif.delete()

    return Notification.objects.create(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


def get_user_notifications(user_id, limit=20):
    """Получает последние limit уведомлений пользователя"""
    return Notification.objects.filter(user_id=user_id)[:limit]


def mark_notification_as_read(notification_id):
    """Отмечает уведомление как прочитанное"""
    Notification.objects.filter(id=notification_id).update(is_read=True)


def mark_all_notifications_as_read(user_id):
    """Отмечает все уведомления пользователя как прочитанные"""
    Notification.objects.filter(user_id=user_id).update(is_read=True)


def get_unread_count(user_id):
    """Возвращает количество непрочитанных уведомлений"""
    return Notification.objects.filter(user_id=user_id, is_read=False).count()


def cleanup_old_notifications(days=30):
    """Удаляет уведомления старше указанного количества дней"""
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff_date).delete()
    return deleted_count
