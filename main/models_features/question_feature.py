from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    subject = models.CharField(max_length=50, default='general')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


def create_question(user_id, title, content, subject='general'):
    """ Создание нового вопроса """

    return Question.objects.create(
        user_id=user_id,
        title=title,
        content=content,
        subject=subject
    ).id


def get_recent_questions(limit=10):
    """ Получение последних вопросов """

    questions = Question.objects.filter(is_deleted=False).select_related('user__profile').annotate(
        answers_count=Count('answers', filter=Q(answers__is_deleted=False))
    ).order_by('-created_at')[:limit]

    return [{
        'id': q.id,
        'title': q.title,
        'content': q.content,
        'subject': q.subject,
        'created_at': q.created_at,
        'user_id': q.user.id,
        'author_name': q.user.profile.nickname or q.user.username,
        'answers_count': q.answers_count
    } for q in questions]


def get_question_by_id(question_id):
    """ Получение вопроса по ID """

    try:
        q = Question.objects.select_related('user__profile').get(id=question_id, is_deleted=False)
        return {
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': q.user.profile.nickname or q.user.username,
        }
    except Question.DoesNotExist:
        return None


def delete_question(question_id, moderator_id):
    """ Удаление вопроса """

    Question.objects.filter(id=question_id).update(is_deleted=True)
