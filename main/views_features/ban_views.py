from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def banned_page(request):
    """Страница для забаненных пользователей"""
    return render(request, 'banned.html', {
        'ban_reason': request.user.profile.ban_reason,
        'banned_at': request.user.profile.banned_at,
        'banned_until': request.user.profile.banned_until,
    })