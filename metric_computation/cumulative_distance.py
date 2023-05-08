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

    Otherwise_parameter = 10
    In_upper_bound = 10

    def __init__(self,
                 distance_to_bug_object: DistanceToBug,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        super().__init__(distance_to_bug_object,
                         program_locations,
                         e_inspect)

    def get_cumulative_distance(self) -> float:
        if len(self._program_locations) == 0:
            return self.Otherwise_parameter

        transformed_list = self._get_transformed_rank_distance_list()

        cumulative_distance = 0

        for index in range(len(transformed_list)):
            current_rec = transformed_list[index]
            current_rank = current_rec[0]
            current_distance = current_rec[1]
            if current_rank > self.In_upper_bound:
                break
            cumulative_distance += current_rank * current_distance

        return cumulative_distance

    @staticmethod
    def _get_average_rank_of_tie(start_index: int, end_index: int) -> float:
        start_loc = start_index + 1
        end_loc = end_index + 1

        e_inspect_of_tie = start_loc + (end_loc - start_loc) / 2

        return e_inspect_of_tie

    def _get_min_distance_of_tie(self, start_index, end_index):
        tie_distance_values = [self._distance_base.get_value(x)
                               for x in self._program_locations[start_index:end_index + 1]]

        min_tie_distance = min(tie_distance_values)

        return min_tie_distance

    def _get_transformed_rank_distance_list(self) -> List[Tuple[float, float]]:
        transformed_list = []

        index = 0
        while index < len(self._program_locations) and index < self._e_inspect:
            current_prog_location = self._program_locations[index]
            start_index, end_index = self._e_inspect_base.get_tied_range(current_prog_location.get_score())
            if start_index == end_index:
                # not in tie
                current_e_inspect = index + 1  # e_inspect counts from 1, not 0.
                current_distance = self._distance_base.get_value(current_prog_location)
                current_rec = (current_e_inspect, current_distance)
                transformed_list.append(current_rec)
                index += 1
            else:
                # in tie
                average_rank_of_tie = self._get_average_rank_of_tie(start_index, end_index)
                min_distance_of_tie = self._get_min_distance_of_tie(start_index, end_index)
                if average_rank_of_tie < self._e_inspect:
                    # not the last tie
                    current_rec = (average_rank_of_tie, min_distance_of_tie)
                    transformed_list.append(current_rec)
                    index = end_index + 1
                else:
                    # the last tie
                    current_rec = (self._e_inspect, min_distance_of_tie)
                    transformed_list.append(current_rec)
                    break

        return transformed_list
