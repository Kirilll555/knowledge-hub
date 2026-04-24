from django.db import models
from django.contrib.auth.models import User


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=20, default='light')
    notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='ru')
    updated_at = models.DateTimeField(auto_now=True)


def get_user_settings(user_id):
    """ Получает настройки пользователя """

    settings, _ = UserSettings.objects.get_or_create(user_id=user_id)
    return {
        'theme': settings.theme,
        'notifications': settings.notifications,
        'language': settings.language,
    }


def update_user_settings(user_id, settings):
    """ Обновляет настройки пользователя """

    UserSettings.objects.update_or_create(
        user_id=user_id,
        defaults={
            'theme': settings.get('theme', 'light'),
            'notifications': settings.get('notifications', True),
            'language': settings.get('language', 'ru'),
        }
    )
