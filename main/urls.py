from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new-question/', views.new_question, name='new_question'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('articles/', views.articles, name='articles'),
    path('moderation/', views.moderation, name='moderation'),
    path('ratings/', views.ratings, name='ratings'),
    path('login/', views.login_page, name='login'),
]