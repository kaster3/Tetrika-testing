import pytest

from task1.solution import sum_two


class TestTask1:
    def test_sum_two(self):
        assert sum_two(1, 2) == 3
        assert sum_two(6, 2) == 8
        assert sum_two(-1, 3) == 2

    def test_sum_raise(self):
        with pytest.raises(TypeError) as context:
            sum_two(2, 2.3)
        assert str(context.value) == "'b' не соответствует типу int"

        with pytest.raises(TypeError):
            sum_two(a=2, b=3.1)

        with pytest.raises(TypeError) as context:
            sum_two(a="2", b=3)
            assert str(context.value) == "'a' не соответствует типу str"


