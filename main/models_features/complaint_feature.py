from django.db import models
from django.contrib.auth.models import User
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer


class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('spam', 'Спам'),
        ('offensive', 'Оскорбление'),
        ('incorrect', 'Неверная информация'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


def create_complaint(user_id, complaint_type, reason, question_id=None, answer_id=None):
    """ Создаёт жалобу """

    Complaint.objects.create(
        user_id=user_id,
        complaint_type=complaint_type,
        question_id=question_id,
        answer_id=answer_id,
        reason=reason
    )


def get_all_complaints(resolved=False):
    """ Получает все жалобы """

    complaints = Complaint.objects.filter(is_resolved=resolved).order_by('-created_at')
    return [(c.id, c.user_id, c.complaint_type, c.question_id, c.answer_id, c.reason, c.created_at, c.is_resolved)
            for c in complaints]


def resolve_complaint(complaint_id, resolved_by):
    """ Отмечает жалобу как решённую """

    Complaint.objects.filter(id=complaint_id).update(is_resolved=True)
