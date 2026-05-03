from django.db import models
from django.contrib.auth.models import User
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer


class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('spam', 'Спам'),
        ('offensive', 'Оскорбление'),
        ('incorrect', 'Неверная информация'),
        ('user_behavior', 'Плохое поведение пользователя'),
        ('other', 'Другое'),
    ]
    
    TARGET_TYPES = [
        ('question', 'Вопрос'),
        ('answer', 'Ответ'),
        ('user', 'Пользователь'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES, default='question')
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='complaints_against')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    description = models.TextField(blank=True, help_text="Дополнительное описание претензии")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.target_type == 'user':
            return f"Жалоба от {self.user.username} на пользователя {self.target_user.username}"
        elif self.question:
            return f"Жалоба от {self.user.username} на вопрос #{self.question_id}"
        else:
            return f"Жалоба от {self.user.username} на ответ #{self.answer_id}"


def create_complaint(user_id, complaint_type, reason, description='', target_type='question', target_user_id=None, question_id=None, answer_id=None):
    """Создаёт жалобу"""
    return Complaint.objects.create(
        user_id=user_id,
        target_type=target_type,
        complaint_type=complaint_type,
        target_user_id=target_user_id,
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
