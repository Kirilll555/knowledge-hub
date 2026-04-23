from django.shortcuts import render
from django.db.models import Q, Count
from main.models_features import Question


def search_question(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        questions = Question.objects.filter(
            is_deleted=False
        ).select_related('user__profile').annotate(
            answers_count=Count('answers', filter=Q(answers__is_deleted=False))
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(subject__icontains=query)
        ).order_by('-created_at')

        results = [{
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': q.user.profile.nickname or q.user.username,
            'answers_count': q.answers_count
        } for q in questions]

    return render(request, 'search_question.html', {
        'question': query,
        'results': results,
    })