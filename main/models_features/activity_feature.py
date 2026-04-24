from django.db import models
from django.contrib.auth.models import User
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


def add_activity(user_id, activity_type, question_id=None, answer_id=None, metadata=None):
    """ Добавляет запись об активности пользователя """

    UserActivity.objects.create(
        user_id=user_id,
        activity_type=activity_type,
        question_id=question_id,
        answer_id=answer_id,
        metadata=metadata or ''
    )


def get_user_activities(user_id, limit=50):
    """ Получает последние активности пользователя """

    activities = UserActivity.objects.filter(user_id=user_id).order_by('-created_at')[:limit]

    result = []
    for a in activities:
        item = {
            'id': a.id,
            'activity_type': a.activity_type,
            'question_id': a.question_id,
            'answer_id': a.answer_id,
            'metadata': a.metadata,
            'created_at': a.created_at,
        }
        if a.question_id:
            try:
                q = Question.objects.get(id=a.question_id)
                item['question_title'] = q.title
            except Question.DoesNotExist:
                pass
        result.append(item)

    return result
