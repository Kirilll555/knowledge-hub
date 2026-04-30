from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from main.models_features.settings_feature import get_user_settings


def send_notification(user_id, subject, message, html_message=None):
    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            print(f"[NOTIFICATION] User {user.username} has no email")
            return False

        settings_dict = get_user_settings(user_id)

        if not settings_dict.get('notifications', True):
            print(f"[NOTIFICATION] Notifications disabled for user {user.username}")
            return False

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"[NOTIFICATION] Email sent to {user.email}")
        return True

    except User.DoesNotExist:
        print(f"[NOTIFICATION ERROR] User {user_id} not found")
        return False
    except Exception as e:
        print(f"[NOTIFICATION ERROR] {e}")
        return False


def send_answer_notification(question_author_id, answer_author_name, question_title, question_id):
    question_url = f"/question/{question_id}/"

    subject = f"📢 Новый ответ на вопрос: {question_title[:50]}"

    message = f"""
Здравствуйте!

Пользователь {answer_author_name} ответил на ваш вопрос "{question_title}"

Посмотреть ответ: http://localhost:8000{question_url}

---
Knowledge Hub
    """

    send_notification(
        user_id=question_author_id,
        subject=subject,
        message=message,
        html_message=None
    )