import functools
from typing import Callable


def strict(func) -> Callable:
    @functools.wraps(func)
    def wrapped(*args, **kwargs) -> Callable:
        annotations = func.__annotations__
        #  делаем арги кваргами и все в общий словарь для общей проверки
        all_kwargs = {**dict(zip(annotations.keys(), args)), **kwargs}

        for arg_name, expected_type in annotations.items():
            if arg_name in all_kwargs:
                if not isinstance(all_kwargs[arg_name], expected_type):
                    raise TypeError(f"'{arg_name}' не соответствует типу {expected_type.__name__}")

        result = func(*args, **kwargs)
        return result
    return wrapped


@strict
def sum_two(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print(sum_two(1, 2))  # >>> 3
    print(sum_two(1, 2.4))  # >>> TypeError
    print(sum_two(a=1, b=2))
    print(sum_two(a=1, b=2.4))  # >>> TypeError