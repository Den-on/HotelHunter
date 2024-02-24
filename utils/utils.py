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


def counter():
    count = 0

    def func():
        nonlocal count
        count += 1
        return count
    return func
