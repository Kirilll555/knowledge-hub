import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models_features.question_feature import Question
from datetime import datetime, timedelta

# Удалить вопросы старше 30 дней
cutoff_date = datetime.now() - timedelta(days=30)
deleted, _ = Question.objects.filter(
    created_at__lt=cutoff_date,
    is_deleted=True
).delete()
print(f"Удалено старых удаленных вопросов: {deleted}")

# Удалить вопросы конкретного пользователя
deleted, _ = Question.objects.filter(user__username='bad_user').delete()
print(f"Удалено вопросов пользователя: {deleted}")