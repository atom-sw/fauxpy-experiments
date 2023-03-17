from typing import List, Dict

from entity_type import ScoredStatement
from our_base_types import DistanceBase, TechniqueBugOverallBase


class SvCompScoreForBug(DistanceBase):
    """
    S_b(L) is defined as the "best" score with
    respect to any of the locations
    corresponding to b: S_b(L) = max_{L_k in b} S(L, L_k).
    """

    N_for_sv_comp_score = 10

    def __init__(self,
                 buggy_line_names: List[str],
                 buggy_module_sizes: Dict[str, int]):
        super().__init__(buggy_line_names,
                         buggy_module_sizes)

    def get_value(self, program_location: ScoredStatement):
        return self._get_sv_comp_best_score_for_bug(program_location)

    def _get_sv_comp_best_score_for_bug(self, program_location: ScoredStatement) -> float:
        sv_comp_best_score_for_bug_list = []
        for item in self._buggy_line_names:
            current_score = self._get_sv_comp_score(item, program_location)
            sv_comp_best_score_for_bug_list.append(current_score)

        sv_comp_best_score_for_bug = max(sv_comp_best_score_for_bug_list)

        return sv_comp_best_score_for_bug

    def _get_sv_comp_score(self,
                           buggy_line_name: str,
                           program_location: ScoredStatement) -> float:
        """
        The score S(L, L_2) between two program locations L and L_2.
        In this implementation, the first one must be a line in ground truth.
        """

        d_distance = self._get_line_to_line_distance(buggy_line_name, program_location)

        if d_distance == 0:
            return self.N_for_sv_comp_score
        else:
            return -1 * d_distance


# TODO: what to do if the list is empty?
class TechniqueBugSvCompOverallScore(TechniqueBugOverallBase):
    def __init__(self,
                 sv_comp_score_bug_obj: SvCompScoreForBug,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        super().__init__(sv_comp_score_bug_obj,
                         program_locations,
                         e_inspect)

    def get_sv_comp_overall_score(self) -> float:
        # M(f, b) counts from 1, not 0.
        m_of_technique_and_bug = self._get_m_of_technique_and_bug()

        sv_comp_best_score_list = []

        for index in range(0, m_of_technique_and_bug):
            current_prog_location = self._program_locations[index]
            start_index, end_index = self._e_inspect_base.get_tied_range(current_prog_location.get_score())
            k = index + 1  # counts from 1, not 0.
            if start_index == end_index:
                # not in tie
                # S_b(L_k) − k − 1
                best_score = self._distance_base.get_value(current_prog_location) - k - 1
                sv_comp_best_score_list.append(best_score)
            else:
                # in tie
                value_tie_average = self._get_average_value_of_tie(start_index, end_index)
                best_score = value_tie_average - k - 1
                sv_comp_best_score_list.append(best_score)

        if len(sv_comp_best_score_list) == 0:
            return -10
        else:
            sv_comp_overall_score = max(sv_comp_best_score_list)

        return sv_comp_overall_score
