"""
Модуль data_processing
- - - - - - - - - - - -
Содержит утилиты для предобработки входных данных перед подачей в ML-модель.

Экспортируемые функции:
- preprocess(features) -> list[float]
    Выполняет простую нормализацию (min-max) входного вектора признаков.
    Возвращает список чисел в диапазоне [0.0, 1.0].

Параметры и возвращаемые значения:
- features: Iterable[float]
    Последовательность числовых признаков (список/кортеж/итератор).
- return: list[float]
    Нормализованный список признаков.

Исключения:
- ValueError: если передан пустой итерабель (нет признаков).

Примеры:
>>> preprocess([1.0, 2.0, 3.0])
[0.0, 0.5, 1.0]

>>> preprocess([5.0, 5.0])
[0.0, 0.0]
"""

from collections.abc import Iterable


def preprocess(features: Iterable[float]) -> list[float]:
    """
    Преобразует входную последовательность числовых признаков в нормализованный вектор.

    Реализация: min-max нормализация каждого элемента:
        x' = (x - min) / (max - min)
    Если все значения равны (max == min), возвращается список нулей той же длины.

    Args:
        features: Iterable[float] — входные числовые признаки.

    Returns:
        List[float] — нормализованный список признаков в диапазоне [0.0, 1.0].

    Raises:
        ValueError: если features пустой (нет элементов).
    """
    xs = list(features)
    if not xs:
        raise ValueError("No features provided")
    mn = min(xs)
    mx = max(xs)
    if mx == mn:
        return [0.0 for _ in xs]
    return [(x - mn) / (mx - mn) for x in xs]
