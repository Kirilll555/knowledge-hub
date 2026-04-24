"""
Взаимодействие страниц
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from main.views_features.base import (index, profile, question_detail, ask_ai, search_question,
                                      register, login_view, logout_view, ask_question,
                                      add_answer, rate_answer, submit_complaint, moderation_panel,
                                      resolve_complaint)
from main.views_features.base import settings

urlpatterns = [
    path("", index, name="index"),
    path("profile/<str:username>/", profile, name="profile"),
    path("profile/", profile, name="profile"),
    path("question/<int:question_id>/", question_detail, name="question_detail"),
    path("question/", question_detail, name="question"),
    path('search/', search_question, name='search_question'),
    path("settings/", settings, name="settings"),
    path('rate-answer/<int:answer_id>/', rate_answer, name='rate_answer'),

    # АУТЕНТИФИКАЦИЯ
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # ВОПРОСЫ
    path("ask/", ask_question, name="ask"),
    path("ask_ai/", ask_ai, name="ask_ai"),

    # API для AJAX
    path("api/answer/<int:question_id>/", add_answer, name="add_answer"),
    path("api/complaint/", submit_complaint, name="submit_complaint"),

    # МОДЕРАЦИЯ
    path("moderation/", moderation_panel, name="moderation"),
    path("moderation/resolve/<int:complaint_id>/", resolve_complaint, name="resolve_complaint"),
]
