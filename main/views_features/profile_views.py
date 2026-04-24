from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from main.models_features import get_profile, save_profile, get_user_settings, update_user_settings, get_user_activities
from main.utils.validators import validate_positive_integer
from .helpers import get_menu


def profile(request, username):
    """ Страница профиля пользователя """

    from django.contrib.auth.models import User
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, '404.html', {'menu': get_menu(request)}, status=404)

    profile_data = get_profile(user.id)
    activities = get_user_activities(user.id, limit=50)

    return render(request, 'profile.html', {
        'profile_user': user,
        'profile_data': profile_data,
        'activities': activities,
        'menu': get_menu(request),
        'current_user': request.user
    })


@login_required()
def settings(request):
    """ Страница настроек пользователя """

    if not request.user.is_authenticated:
        return render(request, 'settings.html', {'user': request.user})

    settings_data = get_user_settings(request.user.id)
    profile_data = get_profile(request.user.id)
    errors = {}

    if request.method == 'POST':
        age_value = request.POST.get('age', '').strip()
        age, age_error = validate_positive_integer(age_value, 'Возраст')
        if age_error:
            errors['age'] = age_error

        if errors:
            return render(request, 'settings.html', {
                'settings': settings_data,
                'profile': profile_data,
                'user': request.user,
                'errors': errors,
                'form_data': request.POST
            })

        new_settings = {
            'theme': request.POST.get('theme', 'light'),
            'notifications': request.POST.get('notifications') == 'on',
            'language': request.POST.get('language', 'ru'),
        }
        update_user_settings(request.user.id, new_settings)

        profile_update = {
            'nickname': request.POST.get('nickname', ''),
            'age': age,
            'hobby': request.POST.get('hobby', ''),
            'main_subject': request.POST.get('main_subject', 'physics'),
        }
        save_profile(request.user.id, request.user.username, profile_update)

        email = request.POST.get('email', '').strip()
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()

        return redirect('/settings/?saved=1')

    return render(request, 'settings.html', {
        'settings': settings_data,
        'profile': profile_data,
        'user': request.user,
        'saved': request.GET.get('saved'),
        'errors': errors
    })
