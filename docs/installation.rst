Установка
==========

Предварительные требования
--------------------------

- Python 3.8+
- pip (менеджер пакетов Python)
- Git
- Виртуальное окружение (venv)

Пошаговая установка
--------------------

1. Клонируйте репозиторий
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone <repository-url>
    cd knowledge-hub

2. Создайте виртуальное окружение
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

На Windows::

    python -m venv .venv
    .venv\Scripts\activate

На Linux/macOS::

    python3 -m venv .venv
    source .venv/bin/activate

3. Установите зависимости
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -r requirements.txt

Для разработки::

    pip install -r requirements-dev.txt

4. Настройте переменные окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Скопируйте и отредактируйте файл ``.env``::

    cp .env.example .env

Обязательные переменные::

    DEBUG=True
    SECRET_KEY=your-secret-key-here
    DATABASE_URL=sqlite:///db.sqlite3

5. Примените миграции
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py migrate

6. Создайте суперпользователя
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py createsuperuser

Введите:
- Имя пользователя (username)
- Email адрес
- Пароль

7. Запустите сервер
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python manage.py runserver

Откройте в браузере: http://localhost:8000/

Администратор доступен по: http://localhost:8000/admin/

Решение проблем
---------------

**Проблема**: ImportError: No module named 'django'

**Решение**::

    pip install -r requirements.txt

**Проблема**: OSError: [Errno 48] Address already in use

**Решение**::

    python manage.py runserver 8001

**Проблема**: Миграции не применяются

**Решение**::

    python manage.py migrate --run-syncdb
