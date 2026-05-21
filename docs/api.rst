API Документация
================

URL Маршруты
------------

Основные маршруты определены в ``config/urls.py`` и ``main/urls.py``

Главная страница
~~~~~~~~~~~~~~~~

- **GET /** - Главная страница
- **GET /search/** - Поиск вопросов

Вопросы
~~~~~~~

- **GET /questions/** - Список всех вопросов
- **GET /question/<id>/** - Просмотр вопроса
- **POST /question/create/** - Создание вопроса
- **POST /question/<id>/edit/** - Редактирование
- **POST /question/<id>/delete/** - Удаление

Ответы
~~~~~~

- **POST /question/<id>/answer/** - Создание ответа
- **POST /answer/<id>/edit/** - Редактирование ответа
- **POST /answer/<id>/delete/** - Удаление ответа

Оценки
~~~~~~

- **POST /answer/<id>/upvote/** - Положительная оценка (👍)
- **POST /answer/<id>/downvote/** - Отрицательная оценка (👎)

Аутентификация
~~~~~~~~~~~~~~

- **GET /login/** - Страница входа
- **POST /login/** - Вход в систему
- **GET /logout/** - Выход
- **GET /register/** - Страница регистрации
- **POST /register/** - Регистрация

Профили
~~~~~~~

- **GET /profile/<username>/** - Просмотр профиля
- **GET /profile/edit/** - Редактирование профиля
- **POST /profile/edit/** - Сохранение изменений

Модерация
~~~~~~~~~

- **GET /complaints/** - Список жалоб (модератор)
- **POST /complaint/create/** - Создание жалобы
- **POST /complaint/<id>/review/** - Рецензирование жалобы

Блокировка
~~~~~~~~~~

- **POST /user/<id>/ban/** - Блокировка пользователя
- **GET /bans/** - Список заблокированных

AI
~~

- **POST /ask-ai/** - Получить ответ от AI
- **GET /ai/history/** - История AI ответов

Примеры запросов
----------------

Создать вопрос
~~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X POST http://localhost:8000/question/create/ \
      -H "Content-Type: application/json" \
      -d '{
        "title": "Как использовать Django?",
        "content": "Я начинающий разработчик"
      }'

Создать ответ
~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X POST http://localhost:8000/question/1/answer/ \
      -H "Content-Type: application/json" \
      -d '{
        "content": "Вот отличный туториал по Django"
      }'

Оценить ответ
~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X POST http://localhost:8000/answer/1/upvote/ \
      -H "Content-Type: application/json"

Получить профиль
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl http://localhost:8000/profile/john/

Коды ответов HTTP
------------------

- **200 OK** - Успешный запрос
- **201 Created** - Ресурс создан
- **204 No Content** - Успешное удаление
- **400 Bad Request** - Ошибка в параметрах
- **401 Unauthorized** - Нужна аутентификация
- **403 Forbidden** - Доступ запрещён
- **404 Not Found** - Ресурс не найден
- **500 Server Error** - Ошибка сервера
