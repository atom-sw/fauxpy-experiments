from typing import List, Dict, Tuple

from entity_type import ScoredStatement


class Distance:
    """
    The distance D(L1, L2) between two program locations L1, L2.
    """

    def __init__(self,
                 buggy_line_names: List[str],
                 buggy_module_sizes: Dict[str, int]):
        self._buggy_line_names = buggy_line_names
        self._buggy_module_sizes = buggy_module_sizes

    def get_buggy_line_names(self):
        return self._buggy_line_names

    def _get_line_to_line_distance(self,
                                   buggy_line_name: str,
                                   program_location: ScoredStatement) -> float:
        """
        In this implementation, the first one must be a line in ground truth.
        """

        (buggy_package,
         buggy_module,
         buggy_line_number) = self._get_buggy_line_name_components(buggy_line_name)

        if buggy_package != program_location.get_package():
            return 10

        if buggy_module != program_location.get_module():
            return 5

        if buggy_package == "":
            module_path = buggy_module
        else:
            module_path = f"{buggy_package}/{buggy_module}"

        module_size = self._buggy_module_sizes[module_path]
        other_line_num = program_location.get_line_number()

        distance_value = abs(buggy_line_number - other_line_num) / float(module_size)

        return distance_value

    @staticmethod
    def _get_buggy_line_name_components(buggy_line_name: str) -> Tuple[str, str, int]:
        name_parts = buggy_line_name.split("::")
        path_part = name_parts[0]
        path_part_segments = path_part.split("/")
        package_path = "/".join(path_part_segments[:-1])
        module_name = path_part_segments[-1]
        line_number = int(name_parts[1])

        return package_path, module_name, line_number
