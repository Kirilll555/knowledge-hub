import re


def format_answer(text):
    """Подготавливает текст для отображения"""
    if not text:
        return text

    text = text.replace('\n', '<br>')

    return text
