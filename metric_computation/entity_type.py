from abc import abstractmethod
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

    @abstractmethod
    def get_entity_name(self):
        pass


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

    def get_package(self) -> str:
        file_path_parts = self._file_path.split("/")
        package_path = "/".join(file_path_parts[:-1])
        return package_path

    def get_module(self) -> str:
        file_path_parts = self._file_path.split("/")
        module_path = file_path_parts[-1]
        return module_path

    def get_entity_name(self) -> str:
        return f"{self._file_path}::{self._line_number}"

    def set_score(self, val: float):
        self._score = val


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

    def get_function_name(self):
        return self._function_name

    def get_function_range(self):
        return self._function_range

    def get_entity_name(self) -> str:
        return f"{self._file_path}::{self._function_name}::{self._function_range[0]}::{self._function_range[1]}"


class ScoredModule(ScoredEntity):
    def __init__(self, file_path: str, score: float):
        super().__init__(file_path, score)

    def _pretty_representation(self):
        return f"{self._file_path} S:{self._score}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()

    def get_entity_name(self):
        return self.get_file_path()
