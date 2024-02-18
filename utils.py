def is_int(num: str) -> bool:
    """
    Функция принимает на вход строку
    Возвращает:
     True, если является числом
     False, если числом не является
    :param num:
    :return:
    """
    try:
        int(num)
        return True
    except ValueError:
        return False
