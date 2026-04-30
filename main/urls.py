from django.urls import path
from main.views_features.moderation_views import complaints_list, resolve_complaint, moderate_panel
from main.views_features.notification_views import get_notifications, mark_read, mark_all_read
from main.views_features.complaint_views import create_complaint_api
from main.views_features import (
    index, register, login_view, logout_view, profile, settings,
    ask_question, question_detail, add_answer, rate_answer_view,
    search_question, search_question_api, ask_ai, create_ai_session, delete_ai_session, rename_ai_session,
    submit_complaint,
    moderate_resolve_complaint,
    moderate_delete_question, moderate_delete_answer,
    moderate_ban_user, moderate_unban_user,
    moderate_set_moderator, moderate_remove_moderator
)

urlpatterns = [
    # Основные страницы
    path('', index, name='index'),
    path('register/', register, name='register'),
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
    path('search/api/', search_question_api, name='search_question_api'),

    # AI
    path('ask_ai/', ask_ai, name='ask_ai'),
    path('ask_ai/<int:session_id>/', ask_ai, name='ask_ai'),
    path('ask_ai/create/', create_ai_session, name='create_ai_session'),
    path('ask_ai/delete/<int:session_id>/', delete_ai_session, name='delete_ai_session'),
    path('ask_ai/rename/<int:session_id>/', rename_ai_session, name='rename_ai_session'),

    # Жалобы
    path('submit_complaint/', submit_complaint, name='submit_complaint'),

    # Модерация
    path('moderation/', moderate_panel, name='moderation'),
    path('moderation/resolve/<int:complaint_id>/', moderate_resolve_complaint, name='moderate_resolve'),
    path('moderation/delete_question/', moderate_delete_question, name='moderate_delete_question'),
    path('moderation/delete_answer/', moderate_delete_answer, name='moderate_delete_answer'),
    path('moderation/ban_user/', moderate_ban_user, name='moderate_ban_user'),
    path('moderation/unban_user/', moderate_unban_user, name='moderate_unban_user'),
    path('moderation/set_moderator/', moderate_set_moderator, name='moderate_set_moderator'),
    path('moderation/remove_moderator/', moderate_remove_moderator, name='moderate_remove_moderator'),
    path('moderation/complaints/', complaints_list, name='complaints_list'),
    path('moderation/complaints/<int:complaint_id>/resolve/', resolve_complaint, name='resolve_complaint'),

    # API уведомления
    path('api/notifications/', get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', mark_read, name='mark_read'),
    path('api/notifications/mark-all-read/', mark_all_read, name='mark_all_read'),

    # API жалобы
    path('api/complaints/create/', create_complaint_api, name='create_complaint'),
]