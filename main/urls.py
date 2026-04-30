from django.urls import path
from main.views_features.notification_views import get_notifications, mark_read, mark_all_read
from main.views_features.complaint_views import create_complaint_api
from main.views_features.moderation_views import complaints_list, resolve_complaint, moderate_panel, moderate_ban_user, moderate_unban_user
from main.views_features.auth_views import index, register_view, login_view, logout_view, profile, settings
from main.views_features.question_views import ask_question, question_detail, add_answer, rate_answer_view
from main.views_features.ai_views import search_question, ask_ai, create_ai_session, delete_ai_session, rename_ai_session

urlpatterns = [
    # Основные страницы
    path('', index, name='index'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/<str:username>/', profile, name='profile'),
    path('settings/', settings, name='settings'),
    
    # Вопросы и ответы
    path('ask/', ask_question, name='ask'),
    path('question/<int:question_id>/', question_detail, name='question_detail'),
    path('add_answer/<int:question_id>/', add_answer, name='add_answer'),
    path('rate/<int:answer_id>/', rate_answer_view, name='rate_answer'),
    
    # Поиск
    path('search/', search_question, name='search'),
    
    # AI
    path('ask_ai/', ask_ai, name='ask_ai'),
    path('ask_ai/<int:session_id>/', ask_ai, name='ask_ai'),
    path('ask_ai/create/', create_ai_session, name='create_ai_session'),
    path('ask_ai/delete/<int:session_id>/', delete_ai_session, name='delete_ai_session'),
    path('ask_ai/rename/<int:session_id>/', rename_ai_session, name='rename_ai_session'),
    
    # Модерация
    path('moderation/', moderate_panel, name='moderation'),
    path('moderation/complaints/', complaints_list, name='complaints_list'),
    path('moderation/complaints/<int:complaint_id>/resolve/', resolve_complaint, name='resolve_complaint'),
    path('moderation/ban_user/<int:user_id>/', moderate_ban_user, name='moderate_ban_user'),
    path('moderation/unban_user/<int:user_id>/', moderate_unban_user, name='moderate_unban_user'),
    
    # API
    path('api/notifications/', get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', mark_read, name='mark_read'),
    path('api/notifications/mark-all-read/', mark_all_read, name='mark_all_read'),
    path('api/complaints/create/', create_complaint_api, name='create_complaint'),
]
