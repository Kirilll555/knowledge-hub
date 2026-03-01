from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),

    path('questions/', views.questions, name='questions'),
    path('ask-ai/', views.ask_ai, name='ask_ai'),
    path('ask/', views.ask_question, name='ask'),
    path('comments/', views.comments, name='comments'),
    path('settings/', views.settings, name='settings'),
]