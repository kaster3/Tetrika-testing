from task3.solution import merge_intervals, intersect_intervals


class TestIntervalFunctions:
    def test_merge_intervals(self):
        assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
        assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
        assert merge_intervals([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]
        assert merge_intervals([]) == []

    def test_intersection(self):
        assert intersect_intervals([[1, 2], [3, 5]], [[1, 6]]) == [[1, 2], [3, 5]]
        assert intersect_intervals(
            [[1, 3], [2, 6], [8, 10], [15, 18]],
            [[1, 15]]
        ) == [[1, 3], [2, 6], [8, 10], [15, 15]]