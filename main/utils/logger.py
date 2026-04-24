import logging
from functools import wraps

moderation_logger = logging.getLogger('main.moderation')
ai_logger = logging.getLogger('main.ai')
auth_logger = logging.getLogger('main.auth')
db_logger = logging.getLogger('main.db')
main_logger = logging.getLogger('main')


def log_moderation(moderator, action, target=None, reason=''):
    """Логирование действий модерации"""

    extra = {
        'user': moderator.username if hasattr(moderator, 'username') else str(moderator),
        'action': action,
        'target': str(target) if target else 'None',
        'reason': reason,
    }

    message = f"Модератор {extra['user']} совершил действие: {action}"
    if target:
        message += f" | Цель: {target}"
    if reason:
        message += f" | Причина: {reason}"

    moderation_logger.info(message, extra=extra)


def log_ai(user, question, answer='', success=True, error=None):
    """Логирование запросов к ИИ"""

    extra = {
        'user': user.username if user and hasattr(user, 'username') else 'Anonymous',
        'question': question[:200] if question else '',
        'answer': answer[:200] if answer else '',
        'success': success,
    }

    status = "Успешно" if success else "Ошибка"
    message = f"ИИ запрос от {extra['user']} ({status}): {question[:100] if question else 'empty'}"

    if error:
        message += f" | Ошибка: {error}"

    ai_logger.info(message, extra=extra)


def log_auth(user, action, success=True):
    """Логирование авторизации и регистрации"""

    extra = {
        'user': user if isinstance(user, str) else (user.username if hasattr(user, 'username') else str(user)),
        'action': action,
        'success': success,
    }

    status = "успешно" if success else "неудачно"
    message = f"{action.capitalize()} пользователя {extra['user']} ({status})"

    auth_logger.info(message, extra=extra)


def log_db(operation, model, obj_id=None):
    """Логирование операций с БД"""

    message = f"DB: {operation} | Модель: {model}"
    if obj_id:
        message += f" | ID: {obj_id}"

    db_logger.debug(message)


def log_error(error, location='', user=None):
    """Логирование ошибок"""

    extra = {
        'user': user.username if user and hasattr(user, 'username') else 'Anonymous',
        'location': location,
    }

    message = f"Ошибка в {location}: {str(error)}"

    main_logger.error(message, exc_info=True, extra=extra)


def log_function_call(logger=main_logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Вызов функции: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Функция {func.__name__} завершена успешно")
                return result
            except Exception as e:
                logger.error(f"Ошибка в функции {func.__name__}: {str(e)}", exc_info=True)
                raise

        return wrapper

    return decorator
