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


class QuestionView(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')


def create_question(user_id, title, content, subject='general'):
    return Question.objects.create(
        user_id=user_id,
        title=title,
        content=content,
        subject=subject
    ).id


def get_recent_questions(limit=10):
    questions = Question.objects.filter(is_deleted=False).select_related('user__profile').annotate(
        answers_count=Count('answers', filter=Q(answers__is_deleted=False)),
        views_count=Count('views', distinct=True)
    ).order_by('-created_at')[:limit]

    result = []
    for q in questions:
        author_name = q.user.username
        try:
            if q.user.profile:
                author_name = q.user.profile.nickname or q.user.username
        except:
            pass
        result.append({
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': author_name,
            'author_username': q.user.username,
            'answers_count': q.answers_count,
            'views_count': q.views_count
        })
    return result


def get_question_by_id(question_id):
    try:
        q = Question.objects.select_related('user', 'user__profile').annotate(
            views_count=Count('views', distinct=True)
        ).get(id=question_id, is_deleted=False)
        author_name = q.user.username
        try:
            if q.user.profile:
                author_name = q.user.profile.nickname or q.user.username
        except:
            pass
        return {
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': author_name,
            'author_username': q.user.username,
            'views_count': q.views_count,
        }
    except Question.DoesNotExist:
        return None


def add_view(question_id, user_id=None):
    """Добавляет просмотр вопроса (только один просмотр на пользователя)"""
    if question_id:
        QuestionView.objects.get_or_create(
            question_id=question_id,
            user_id=user_id
        )


def get_views_count(question_id):
    """Получает количество уникальных просмотров"""
    return QuestionView.objects.filter(question_id=question_id).count()


def delete_question(question_id, moderator_id):
    Question.objects.filter(id=question_id).update(is_deleted=True)