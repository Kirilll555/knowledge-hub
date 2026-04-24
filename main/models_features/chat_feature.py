from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_sessions')
    title = models.CharField(max_length=200, blank=True, default='Новый диалог')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


def get_user_sessions(user_id):
    return ChatSession.objects.filter(user_id=user_id).order_by('-updated_at')


def get_session_messages(session_id):
    return ChatMessage.objects.filter(session_id=session_id)


def save_message(session_id, role, content):
    return ChatMessage.objects.create(
        session_id=session_id,
        role=role,
        content=content
    )


def update_session_title(session_id, title=None):
    if not title:
        first_message = ChatMessage.objects.filter(session_id=session_id, role='user').first()
        if first_message:
            title = first_message.content[:50] + ('...' if len(first_message.content) > 50 else '')
        else:
            title = 'Новый диалог'
    ChatSession.objects.filter(id=session_id).update(title=title)


def delete_session(session_id, user_id):
    ChatSession.objects.filter(id=session_id, user_id=user_id).delete()
