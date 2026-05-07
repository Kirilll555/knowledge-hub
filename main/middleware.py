from django.shortcuts import render
from django.utils import timezone


class BanCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                # Проверяем только если пользователь действительно забанен
                if profile.is_banned and profile.is_banned is True:
                    # Проверяем срок бана
                    if profile.banned_until and profile.banned_until < timezone.now():
                        profile.is_banned = False
                        profile.banned_until = None
                        profile.save()
                    else:
                        # Разрешаем только logout
                        if request.path not in ['/logout/', '/banned/']:
                            return render(request, 'banned.html', {
                                'ban_reason': profile.ban_reason,
                                'banned_at': profile.banned_at,
                                'banned_until': profile.banned_until,
                            })
            except Exception as e:
                print(f"Middleware error: {e}")
                pass
        
        return self.get_response(request)
