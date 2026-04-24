import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.models_features import create_complaint, add_activity


@login_required
@csrf_exempt
def submit_complaint(request):
    """ Отправка жалобы """

    if request.method == 'POST':
        data = json.loads(request.body) if request.body else request.POST
        complaint_type = data.get('type')
        reason = data.get('reason', '').strip()
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')

        if not reason:
            return JsonResponse({'success': False, 'error': 'Укажите причину жалобы'})

        create_complaint(request.user.id, complaint_type, reason, question_id, answer_id)
        add_activity(request.user.id, 'complaint', metadata=f"Жалоба на {complaint_type}")

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
