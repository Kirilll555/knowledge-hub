Архитектура
===========

Общее описание
--------------

Knowledge Hub использует классическую архитектуру MVC (Model-View-Controller):

::

    Браузер пользователя
           ↓
    Django URLs Router
           ↓
    Django Views
           ↓
    Django Models (ORM)
           ↓
    SQLite Database

Слои приложения
---------------

Models (Модели)
~~~~~~~~~~~~~~~

Основные модели в ``main/models.py``:

- **User**: встроенная модель Django для аутентификации
- **Profile**: расширение User с дополнительной информацией
- **Question**: вопросы пользователей
- **Answer**: ответы на вопросы
- **Rating**: оценки ответов (👍/👎)
- **Complaint**: жалобы на контент
- **Notification**: уведомления пользователям

Views (Представления)
~~~~~~~~~~~~~~~~~~~~~

Views разделены по функциональности в ``main/views_features/``:

- ``main_views.py`` - главная страница, поиск
- ``question_views.py`` - управление вопросами
- ``auth_views.py`` - регистрация, вход, выход
- ``profile_views.py`` - профили пользователей
- ``ai_views.py`` - AI интеграция
- ``moderation_views.py`` - модерация
- ``ban_views.py`` - блокировка пользователей

Models Features (Бизнес-логика)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Дополнительная логика в ``main/models_features/``:

- ``activity_feature.py`` - логирование активности
- ``answer_rating_feature.py`` - система оценок
- ``ai_client.py`` - работа с AI
- ``complaint_feature.py`` - обработка жалоб
- ``moderation_feature.py`` - модерация
- ``profile_feature.py`` - управление профилями

Templates (Шаблоны)
~~~~~~~~~~~~~~~~~~~

HTML шаблоны в ``main/templates/``:

- ``index.html`` - главная страница
- ``question.html`` - страница вопроса
- ``ask.html`` - создание вопроса
- ``profile.html`` - профиль пользователя
- ``login.html`` - вход
- ``register.html`` - регистрация

Styles (Стили)
~~~~~~~~~~~~~~

CSS в ``main/styles/``:

- ``base_styles.html`` - базовые стили
- ``index_styles.html`` - стили главной
- ``question_styles.html`` - стили вопроса
- ``profile_styles.html`` - стили профиля

Utils (Утилиты)
~~~~~~~~~~~~~~~

Вспомогательные функции в ``main/utils/``:

- ``email_notifications.py`` - отправка email
- ``ai_client.py`` - работа с AI моделями
- ``formatter.py`` - форматирование данных
- ``logger.py`` - логирование
- ``validators.py`` - валидация данных

Взаимодействие компонентов
---------------------------

Типичный сценарий создания вопроса:

1. Пользователь заполняет форму в браузере
2. Отправляется POST запрос на ``/question/create/``
3. Django URLs router направляет на ``question_views.create_question()``
4. View проверяет авторизацию и валидирует данные
5. View создает объект Question через ORM (models.py)
6. Django ORM генерирует SQL и сохраняет в БД
7. View логирует действие через ``activity_feature.py``
8. View отправляет email уведомление через ``email_notifications.py``
9. Возвращается ответ в браузер (редирект на вопрос)

Поток данных
~~~~~~~~~~~~

::

    User Input (Form)
         ↓
    URL Router (/question/create/)
         ↓
    View (create_question)
         ↓
    Validator (validators.py)
         ↓
    Model Save (ORM)
         ↓
    Database Insert
         ↓
    Activity Log (activity_feature.py)
         ↓
    Email Notification (email_notifications.py)
         ↓
    Response (Redirect)
         ↓
    Browser Display

Безопасность
~~~~~~~~~~~~

- **CSRF Protection** - встроенная в Django
- **SQL Injection Protection** - через ORM
- **XSS Protection** - через template escaping
- **Authentication** - встроенная в Django
- **Permissions** - проверка прав доступа в views

Масштабируемость
~~~~~~~~~~~~~~~~

Архитектура поддерживает масштабирование:

- ORM позволяет легко переключиться с SQLite на PostgreSQL
- Views отделены от бизнес-логики
- Кеширование можно добавить на любой уровень
- Асинхронные задачи через Celery (если нужно)
