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
    
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    description = models.TextField(blank=True, help_text="Дополнительное описание претензии")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = f"Вопрос #{self.question_id}" if self.question else f"Ответ #{self.answer_id}"
        return f"Жалоба от {self.user.username} на {target}"


def create_complaint(user_id, complaint_type, reason, description='', question_id=None, answer_id=None):
    """Создаёт жалобу"""
    return Complaint.objects.create(
        user_id=user_id,
        complaint_type=complaint_type,
        question_id=question_id,
        answer_id=answer_id,
        reason=reason,
        description=description
    )


def get_all_complaints(status=None):
    """Получает все жалобы с фильтром по статусу"""
    complaints = Complaint.objects.all().order_by('-created_at')
    if status:
        complaints = complaints.filter(status=status)
    return complaints


def resolve_complaint(complaint_id, resolved_by):
    """Отмечает жалобу как решённую (одобренную)"""
    Complaint.objects.filter(id=complaint_id).update(status='approved')


def update_complaint_status(complaint_id, status):
    """Обновляет статус жалобы"""
    Complaint.objects.filter(id=complaint_id).update(status=status)
