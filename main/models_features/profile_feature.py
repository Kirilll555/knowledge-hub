from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(null=True, blank=True)
    hobby = models.CharField(max_length=200, blank=True)
    main_subject = models.CharField(max_length=50, default='physics')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_moderator(self):
        return self.role in ['moderator', 'admin']

    def is_admin(self):
        return self.role == 'admin'


def get_profile(user_id):
    """ Получение профиля пользователя """

    try:
        profile = Profile.objects.select_related('user').get(user_id=user_id)
        return {
            'username': profile.user.username,
            'nickname': profile.nickname or '',
            'age': profile.age,
            'hobby': profile.hobby or '',
            'main_subject': profile.main_subject,
            'role': profile.role,
            'is_banned': profile.is_banned,
            'ban_reason': profile.ban_reason,
        }
    except Profile.DoesNotExist:
        return None


def save_profile(user_id, username, data):
    """ Сохранение или обновление профиля """

    profile, _ = Profile.objects.update_or_create(
        user_id=user_id,
        defaults={
            'nickname': data.get('nickname', ''),
            'age': data.get('age'),
            'hobby': data.get('hobby', ''),
            'main_subject': data.get('main_subject', 'physics'),
            'role': data.get('role', 'user'),
        }
    )
    return True


def ban_user(user_id, moderator_id, reason):
    """ Блокировка пользователя """

    profile = Profile.objects.get(user_id=user_id)
    profile.is_banned = True
    profile.ban_reason = reason
    profile.banned_at = timezone.now()
    profile.save()
    return True


def unban_user(user_id, moderator_id):
    """ Разблокировка пользователя """

    profile = Profile.objects.get(user_id=user_id)
    profile.is_banned = False
    profile.ban_reason = ''
    profile.banned_at = None
    profile.save()
    return True


def set_moderator(user_id, admin_id):
    """ Назначение модератора (только для админа) """

    profile = Profile.objects.get(user_id=user_id)
    profile.role = 'moderator'
    profile.save()
    return True


def remove_moderator(user_id, admin_id):
    """ Снятие модератора (только для админа) """

    profile = Profile.objects.get(user_id=user_id)
    profile.role = 'user'
    profile.save()
    return True


def check_user_access(user):
    """ Проверка доступа пользователя (не заблокирован ли) """

    if not user.is_authenticated:
        return True
    try:
        profile = Profile.objects.get(user=user)
        return not profile.is_banned
    except Profile.DoesNotExist:
        return True


def check_moderator_access(user):
    """ Проверка доступа модератора """

    if not user.is_authenticated:
        return False
    try:
        profile = Profile.objects.get(user=user)
        return profile.is_moderator()
    except Profile.DoesNotExist:
        return False


def check_admin_access(user):
    """ Проверка доступа администратора """

    if not user.is_authenticated:
        return False
    try:
        profile = Profile.objects.get(user=user)
        return profile.is_admin()
    except Profile.DoesNotExist:
        return False
