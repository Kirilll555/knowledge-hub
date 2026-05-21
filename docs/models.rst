Модели данных
=============

Основные модели
---------------

User Model (Django встроенная)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.contrib.auth.models import User
    
    # Встроенные поля:
    # - id
    # - username (имя пользователя)
    # - password (зашифрованный пароль)
    # - email
    # - first_name, last_name
    # - is_active (активен ли)
    # - is_staff (администратор ли)
    # - is_superuser (суперпользователь ли)
    # - date_joined (дата регистрации)
    # - last_login (последний вход)

Profile Model
~~~~~~~~~~~~~

Расширение User модели.

.. code-block:: python

    from main.models import Profile
    
    # Поля:
    # - user (связь с User)
    # - bio (биография)
    # - avatar (аватар)
    # - created_at
    # - updated_at
    # - is_banned (заблокирован ли)
    # - banned_until (дата разблокировки)
    # - ban_reason (причина блокировки)

Question Model
~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Question
    
    # Поля:
    # - user (автор)
    # - title (название)
    # - content (содержание)
    # - created_at
    # - updated_at
    # - is_closed (закрыт ли вопрос)
    # - view_count (количество просмотров)
    # - category (категория)
    # - tags (теги)

Answer Model
~~~~~~~~~~~~

.. code-block:: python

    from main.models import Answer
    
    # Поля:
    # - question (связь с Question)
    # - user (автор ответа)
    # - content (содержание ответа)
    # - created_at
    # - updated_at
    # - is_accepted (принят ли как правильный)
    # - rating (общий рейтинг)

Rating Model
~~~~~~~~~~~~

.. code-block:: python

    from main.models import Rating
    
    # Поля:
    # - answer (связь с Answer)
    # - user (кто оценил)
    # - value (значение: 1 или -1)
    # - created_at

Complaint Model
~~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Complaint
    
    # Поля:
    # - content_type (тип контента)
    # - object_id (ID контента)
    # - user (кто подал жалобу)
    # - reason (причина)
    # - status (статус: open, reviewed, resolved)
    # - created_at
    # - reviewed_at

Notification Model
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Notification
    
    # Поля:
    # - user (получатель)
    # - content (текст)
    # - type (тип: question, answer, rating)
    # - is_read (прочитано ли)
    # - created_at

Диаграмма связей
----------------

::

    User (Django)
      ↓
      ├─ 1:1 → Profile
      ├─ 1:M → Question → Answer → Rating
      ├─ 1:M → Rating
      ├─ 1:M → Complaint
      ├─ 1:M → Notification
      └─ 1:M → ActivityLog

Примеры использования
---------------------

Получить все вопросы
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Question
    
    questions = Question.objects.all()

Получить вопросы пользователя
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.contrib.auth.models import User
    
    user = User.objects.get(username='john')
    questions = user.question_set.all()

Получить ответы на вопрос
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    question = Question.objects.get(id=1)
    answers = question.answer_set.all()

Создать вопрос
~~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Question
    
    question = Question.objects.create(
        user=user,
        title='Мой вопрос',
        content='Содержание'
    )

Создать ответ
~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Answer
    
    answer = Answer.objects.create(
        question=question,
        user=user,
        content='Мой ответ'
    )

Оценить ответ
~~~~~~~~~~~~~~

.. code-block:: python

    from main.models import Rating
    
    rating = Rating.objects.create(
        answer=answer,
        user=user,
        value=1  # положительная оценка
    )

Получить популярные ответы
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.db.models import Sum
    
    top_answers = Answer.objects.annotate(
        total_rating=Sum('rating__value')
    ).order_by('-total_rating')[:10]
