Тестирование
=============

Структура тестов
-----------------

Тесты находятся в папке ``tests/``:

::

    tests/
    ├── test_auth_views.py          # Тесты аутентификации
    ├── test_question_views.py      # Тесты вопросов
    ├── test_complaint_views.py     # Тесты жалоб
    ├── test_helpers.py             # Тесты помощников
    ├── test_main_views.py          # Тесты главной страницы
    ├── test_moderation_views.py    # Тесты модерации
    ├── test_notification.py        # Тесты уведомлений
    ├── test_profile.py             # Тесты профилей
    ├── test_ban_views.py           # Тесты блокировки
    └── test_ai_views.py            # Тесты AI

Запуск тестов
--------------

Запустить все тесты
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py test

Запустить определённый модуль
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py test tests.test_auth_views

Запустить определённый тест
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py test tests.test_auth_views.AuthViewsTestCase.test_login

Запустить с coverage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    coverage run --source='main' manage.py test
    coverage report
    coverage html

Написание тестов
----------------

Простой тест модели
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.test import TestCase
    from django.contrib.auth.models import User
    from main.models import Question

    class QuestionTestCase(TestCase):
        
        def setUp(self):
            """Подготовка данных перед тестом"""
            self.user = User.objects.create_user(
                username='testuser',
                password='testpass123'
            )
        
        def test_create_question(self):
            """Проверить создание вопроса"""
            question = Question.objects.create(
                user=self.user,
                title='Test',
                content='Content'
            )
            self.assertEqual(question.user, self.user)
            self.assertEqual(question.title, 'Test')

Тест view
~~~~~~~~~

.. code-block:: python

    from django.test import TestCase, Client
    from django.urls import reverse

    class LoginTestCase(TestCase):
        
        def setUp(self):
            self.client = Client()
            self.user = User.objects.create_user(
                username='john',
                password='pass123'
            )
        
        def test_login_page(self):
            """Проверить доступ к странице входа"""
            response = self.client.get(reverse('login'))
            self.assertEqual(response.status_code, 200)
        
        def test_login_success(self):
            """Проверить успешный вход"""
            response = self.client.post(
                reverse('login'),
                {'username': 'john', 'password': 'pass123'}
            )
            self.assertEqual(response.status_code, 302)

Best Practices
--------------

✅ **Рекомендуется**:

- Одно утверждение (assert) на тест
- Использовать setUp() для инициализации
- Описательные названия тестов
- Тестировать граничные случаи
- Мокировать внешние зависимости

❌ **Не рекомендуется**:

- Несколько assert'ов в одном тесте
- Зависимости между тестами
- Жёсткие зависимости на файлы
- Тестирование без setUp()
