from django.urls import path
from main.views_features.base import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", index, name="index"),
    path("profile/", profile, name="profile"),
    path("about/", about, name="about"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("question/", question_detail, name="question"),
    path("ask_ai/", ask_ai, name="ask_ai"),
    path("ask/", ask_question, name="ask"),
    path("comments/", comments, name="comments"),
    path("settings/", settings, name="settings"),
]
