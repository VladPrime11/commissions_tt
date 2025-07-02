import time
from functools import wraps


def benchmark(label="Execution time"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            print(f"{label}: {end - start:.4f} seconds")
            return result

        return wrapper

    return decorator
