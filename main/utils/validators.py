def validate_positive_integer(value, field_name):
    """ Валидация поля на положительное целое число """

    if not value or value == '':
        return None, None

    try:
        num = int(value)
        if num <= 0:
            return None, f"{field_name} должен быть положительным числом"
        return num, None
    except (ValueError, TypeError):
        return None, f"{field_name} должен быть целым числом"