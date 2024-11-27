import functools
from typing import Callable


def strict(func) -> Callable:
    @functools.wraps(func)
    def wrapped(*args, **kwargs) -> Callable:
        annotations = func.__annotations__

        for count, (arg_name, expected_type) in enumerate(annotations.items()):
            if count < len(args):
                if not isinstance(args[count], expected_type):
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