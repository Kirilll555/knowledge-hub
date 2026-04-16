from django.urls import path
from main.views_features.base import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", index, name="index"),
    path("profile/", profile, name="profile"),
    path("question/", question_detail, name="question"),
    path('search/', search_question, name='search_question'),
    path("settings/", settings, name="settings"),
]
