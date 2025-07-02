"""
Декоратор для вимірювання часу виконання функцій.
"""

import time
from functools import wraps


def benchmark(label="Execution time"):
    """
    Декоратор що вимірює і виводить час виконання функції.

    Можна використовувати з власною підписом або без неї.
    """

    def decorator(func):
        @wraps(func)  # Зберігає оригінальні метадані функції
        def wrapper(*args, **kwargs):
            # Засікаємо час перед виконанням
            start = time.perf_counter()

            # Виконуємо оригінальну функцію
            result = func(*args, **kwargs)

            # Засікаємо час після виконання
            end = time.perf_counter()

            print(f"{label}: {end - start:.4f} seconds")

            return result

        return wrapper

    return decorator