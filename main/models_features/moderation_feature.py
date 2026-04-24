from django.db import models
from django.contrib.auth.models import User
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer


class ModerationLog(models.Model):
    ACTION_CHOICES = [
        ('delete_question', 'Удаление вопроса'),
        ('delete_answer', 'Удаление ответа'),
        ('ban_user', 'Блокировка пользователя'),
        ('unban_user', 'Разблокировка пользователя'),
        ('set_moderator', 'Назначение модератора'),
        ('remove_moderator', 'Снятие модератора'),
        ('resolve_complaint', 'Решение жалобы'),
    ]

    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='moderation_targets')
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moderator.username} - {self.get_action_display()} - {self.created_at}"


def log_moderation_action(moderator_id, action, target_user_id=None, question_id=None, answer_id=None, reason=''):
    """ Логирование действий модератора """
    return ModerationLog.objects.create(
        moderator_id=moderator_id,
        action=action,
        target_user_id=target_user_id,
        question_id=question_id,
        answer_id=answer_id,
        reason=reason
    )


def delete_question_moderate(question_id, moderator_id, reason=''):
    """ Удаление вопроса модератором """

    try:
        question = Question.objects.get(id=question_id)
        target_user_id = question.user.id
    except Question.DoesNotExist:
        target_user_id = None

    Question.objects.filter(id=question_id).update(is_deleted=True)

    log_moderation_action(
        moderator_id=moderator_id,
        action='delete_question',
        target_user_id=target_user_id,
        question_id=question_id,
        reason=reason,
    )
    return True


def delete_answer_moderate(answer_id, moderator_id, reason=''):
    """ Удаление ответа модератором """

    try:
        answer = Answer.objects.get(id=answer_id)
        target_user_id = answer.user.id
        question_id = answer.question.id
    except Answer.DoesNotExist:
        target_user_id = None
        question_id = None

    Answer.objects.filter(id=answer_id).update(is_deleted=True)

    log_moderation_action(
        moderator_id=moderator_id,
        action='delete_answer',
        target_user_id=target_user_id,
        answer_id=answer_id,
        question_id=question_id,
        reason=reason,
    )
    return True


def get_moderation_logs(limit=100):
    """ Получение логов модерации """

    return ModerationLog.objects.select_related('moderator', 'target_user').order_by('-created_at')[:limit]
