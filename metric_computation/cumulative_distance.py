from typing import List, Dict, Tuple

from entity_type import ScoredStatement
from our_base_types import DistanceBase, TechniqueBugOverallBase


class DistanceToBug(DistanceBase):
    """
    The distance D_b(L) between a program location
    and a bug b is the minimum distance between
    L and any of the locations
    corresponding to b: D_b(L) = min_{L_k in b} D(L, L_k).
    """

    def __init__(self,
                 buggy_line_names: List[str],
                 buggy_module_sizes: Dict[str, int]):
        super().__init__(buggy_line_names,
                         buggy_module_sizes)

    def get_value(self, program_location: ScoredStatement):
        return self._get_d_distance_to_bug(program_location)

    def _get_d_distance_to_bug(self, program_location: ScoredStatement) -> float:
        distance_to_bug_list = []
        for item in self._buggy_line_names:
            current_distance = self._get_line_to_line_distance(item, program_location)
            distance_to_bug_list.append(current_distance)

        min_distance_to_bug = min(distance_to_bug_list)

        return min_distance_to_bug

    @staticmethod
    def _get_buggy_line_name_components(buggy_line_name: str) -> Tuple[str, str, int]:
        name_parts = buggy_line_name.split("::")
        path_part = name_parts[0]
        path_part_segments = path_part.split("/")
        package_path = "/".join(path_part_segments[:-1])
        module_name = path_part_segments[-1]
        line_number = int(name_parts[1])

        return package_path, module_name, line_number


class TechniqueBugCumulativeDistance(TechniqueBugOverallBase):
    """
    Cumulative distance D(f, b) to each fault localization
    technique f on a bug b is the weighted sum
    of the relevant distances.
    """

    def __init__(self,
                 distance_to_bug_object: DistanceToBug,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        super().__init__(distance_to_bug_object,
                         program_locations,
                         e_inspect)

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
                cumulative_distance += k * self._distance_base.get_value(current_prog_location)
            else:
                # in tie
                distance_tie_avg = self._get_average_value_of_tie(start_index, end_index)
                cumulative_distance += k * distance_tie_avg

        return cumulative_distance
