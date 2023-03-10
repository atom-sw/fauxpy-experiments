from typing import Tuple


class ScoredEntity:
    def __init__(self,
                 file_path: str,
                 score: float):
        self._file_path = file_path
        self._score = score

    def get_score(self):
        return self._score

    def get_file_path(self):
        return self._file_path


class ScoredStatement(ScoredEntity):
    def __init__(self, file_path: str, score: float, line_number: int):
        super().__init__(file_path, score)
        self._line_number = line_number

    def _pretty_representation(self):
        return f"{self._file_path} L:{self._line_number} S:{self._score}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()

    def get_line_number(self) -> int:
        return self._line_number


class ScoredFunction(ScoredEntity):
    def __init__(self, file_path: str, score: float, function_range: Tuple[int, int], function_name: str):
        super().__init__(file_path, score)
        self._function_range = function_range
        self._function_name = function_name

    def _pretty_representation(self):
        return f"{self._file_path} N:{self._function_name} R:{self._function_range} S:{self._score}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()

    def get_function_range(self):
        return self._function_range
