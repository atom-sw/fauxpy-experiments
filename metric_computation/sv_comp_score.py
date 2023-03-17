from typing import List, Dict

from entity_type import ScoredStatement
from literature_metrics import EInspectBase
from our_base_types import DistanceBase


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
        """

        d_distance = self._get_line_to_line_distance(buggy_line_name, program_location)

        if d_distance == 0:
            return self.N_for_sv_comp_score
        else:
            return -1 * d_distance


class TechniqueBugSvCompOverallScore:
    def __init__(self,
                 sv_comp_score_bug_obj: SvCompScoreForBug,
                 program_locations: List[ScoredStatement],
                 e_inspect: float):
        self._sv_comp_score_bug_obj = sv_comp_score_bug_obj
        self._program_locations = program_locations
        self._e_inspect = e_inspect
        self._e_inspect_base = EInspectBase(program_locations,
                                            sv_comp_score_bug_obj.get_buggy_line_names())

    def get_sv_comp_overall_score(self):
        pass
