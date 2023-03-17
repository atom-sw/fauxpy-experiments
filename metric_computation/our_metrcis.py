from typing import List, Dict, Tuple

import mathematics
from entity_type import ScoredStatement
from literature_metrics import EInspectBase

"""
We use ScoredStatement class as program location.
A program location L_k is a triple <p_k, m_k, l_k>, where p_k is
the location’s package (corresponding to a directory within
the project), m_k is the location’s module (corresponding to a
file in p+k), and l_k is the location’s
line number (within m_k).
"""


class DistanceToBug:
    """
    The distance D_b(L) between a program location
    and a bug b is the minimum distance between
    L and any of the locations
    corresponding to b.
    """

    def __init__(self,
                 buggy_line_names: List[str],
                 buggy_module_sizes: Dict[str, int]):
        self._buggy_line_names = buggy_line_names
        self._buggy_module_sizes = buggy_module_sizes

    def get_buggy_line_names(self):
        return self._buggy_line_names

    def get_distance_to_bug(self, program_location: ScoredStatement) -> float:
        distance_to_bug_list = []
        for item in self._buggy_line_names:
            current_distance = self._get_distance(item, program_location)
            distance_to_bug_list.append(current_distance)

        min_distance_to_bug = min(distance_to_bug_list)

        return min_distance_to_bug

    def _get_distance(self,
                      buggy_line_name: str,
                      program_location: ScoredStatement) -> float:
        """
        The distance D(L1, L2) between two program locations L1, L2.
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


class TechniqueBugCumulativeDistance:
    """
    Cumulative distance D(f, b) to each fault localization
    technique f on a bug b is the weighted sum
    of the relevant distances.
    """

    parameter_N = 10

    def __init__(self,
                 distance_to_bug_object: DistanceToBug,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        self._distance_to_bug_object = distance_to_bug_object
        self._program_locations = program_locations
        self._e_inspect = e_inspect
        self._e_inspect_base = EInspectBase(program_locations,
                                            distance_to_bug_object.get_buggy_line_names())

    def get_cumulative_distance(self) -> float:
        # M(f, b) counts from 1, not 0.
        m_of_technique_and_bug = self._get_m_of_technique_and_bug()

        cumulative_distance = 0

        for index in range(0, m_of_technique_and_bug):
            current_prog_location = self._program_locations[index]
            start_index, end_index = self._e_inspect_base.get_tied_range(current_prog_location.get_score())
            k = index + 1  # counts from 1, not 0.
            if start_index == end_index:
                # not in tie
                # k . D_b(L_k)
                cumulative_distance += k * self._distance_to_bug_object.get_distance_to_bug(current_prog_location)
            else:
                # in tie
                distance_tie_avg = self._get_average_distance_tie(start_index, end_index)
                cumulative_distance += k * distance_tie_avg

        return cumulative_distance

    def _get_m_of_technique_and_bug(self) -> int:
        """
        M(f, b) is the smallest 1 <= k <= min(n, N) such
        that D_b(L_k) = 0;
        if D_b(L_k) != 0 for all 1 <= k <= min(n, N), then
        M(f, b) = min(n, N).
        """

        # for min(n, N).
        min_n_N = min(self.parameter_N,
                      len(self._program_locations))

        # for bug locations in a tie we round the e_inspect.
        e_inspect_round = int(round(self._e_inspect))

        # for smallest 1 <= k <= min(n, N) such that D_b(L_k) = 0.
        m_of_technique_and_bug = min(min_n_N,
                                     e_inspect_round)

        return m_of_technique_and_bug

    def _get_average_distance_tie(self,
                                  start_index: int,
                                  end_index: int) -> float:
        tie_distances = []
        for index in range(start_index, end_index + 1):
            current_program_location = self._program_locations[index]
            current_bug_dist = self._distance_to_bug_object.get_distance_to_bug(current_program_location)
            tie_distances.append(current_bug_dist)

        average_tie_distances = mathematics.average(tie_distances)
        return average_tie_distances


def compute_our_metrics(program_locations: List[ScoredStatement],
                        buggy_line_names: List[str],
                        buggy_module_sizes: Dict[str, int],
                        e_inspect: float):
    distance_to_bug_obj = DistanceToBug(buggy_line_names, buggy_module_sizes)
    technique_bug_cumulative_distance_obj = TechniqueBugCumulativeDistance(distance_to_bug_obj, program_locations,
                                                                           e_inspect)
    cumulative_distance = technique_bug_cumulative_distance_obj.get_cumulative_distance()

    return cumulative_distance, 0
