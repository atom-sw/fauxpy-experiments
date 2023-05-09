from abc import abstractmethod
from typing import List, Dict, Tuple

import mathematics
from entity_type import ScoredStatement
from literature_metrics import EInspectBase


class DistanceBase:
    """
    The distance D(L1, L2) between two program locations L1, L2.
    """

    def __init__(self,
                 buggy_line_names: List[str],
                 buggy_module_sizes: Dict[str, int]):
        self._buggy_line_names = buggy_line_names
        self._buggy_module_sizes = buggy_module_sizes

    @abstractmethod
    def get_value(self,
                  program_location: ScoredStatement):
        pass

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

        distance_value = 1 + (abs(buggy_line_number - other_line_num) / float(module_size))

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


class TechniqueBugOverallBase:
    _N_for_function_M = 10

    def __init__(self,
                 distance_base: DistanceBase,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        self._distance_base = distance_base
        self._program_locations = program_locations
        self._e_inspect = e_inspect
        self._e_inspect_base = EInspectBase(program_locations,
                                            distance_base.get_buggy_line_names())

    def _get_m_of_technique_and_bug(self) -> int:
        """
        M(f, b) is the smallest 1 <= k <= min(n, N) such
        that D_b(L_k) = 0;
        if D_b(L_k) != 0 for all 1 <= k <= min(n, N), then
        M(f, b) = min(n, N).
        """

        # for min(n, N).
        min_n_N = min(self._N_for_function_M,
                      len(self._program_locations))

        # for bug locations in a tie we round the e_inspect
        # as parameter m is an integer, which is the upper
        # bound of a summation formula.
        e_inspect_round = int(round(self._e_inspect))

        # for smallest 1 <= k <= min(n, N) such that D_b(L_k) = 0.
        m_of_technique_and_bug = min(min_n_N,
                                     e_inspect_round)

        return m_of_technique_and_bug

    def _get_average_value_of_tie(self,
                                  start_index: int,
                                  end_index: int) -> float:
        tie_values = []
        for index in range(start_index, end_index + 1):
            current_program_location = self._program_locations[index]
            current_bug_value = self._distance_base.get_value(current_program_location)
            tie_values.append(current_bug_value)

        average_tie_values = mathematics.average(tie_values)
        return average_tie_values
