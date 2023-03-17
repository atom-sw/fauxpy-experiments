from typing import List, Dict

from cumulative_distance import DistanceToBug, TechniqueBugCumulativeDistance
from entity_type import ScoredStatement
from sv_comp_score import SvCompScoreForBug, TechniqueBugSvCompOverallScore

"""
We use ScoredStatement class as program location.
A program location L_k is a triple <p_k, m_k, l_k>, where p_k is
the location’s package (corresponding to a directory within
the project), m_k is the location’s module (corresponding to a
file in p_k), and l_k is the location’s
line number (within m_k).
"""


def compute_our_metrics(program_locations: List[ScoredStatement],
                        buggy_line_names: List[str],
                        buggy_module_sizes: Dict[str, int],
                        e_inspect: float):
    distance_to_bug_obj = DistanceToBug(buggy_line_names, buggy_module_sizes)
    technique_bug_cumulative_distance_obj = TechniqueBugCumulativeDistance(distance_to_bug_obj,
                                                                           program_locations,
                                                                           e_inspect)
    cumulative_distance = technique_bug_cumulative_distance_obj.get_cumulative_distance()

    sv_comp_score_bug_obj = SvCompScoreForBug(buggy_line_names, buggy_module_sizes)
    technique_bug_sv_comp_overall_score_obj = TechniqueBugSvCompOverallScore(sv_comp_score_bug_obj,
                                                                             program_locations,
                                                                             e_inspect)
    sv_comp_overall_score = technique_bug_sv_comp_overall_score_obj.get_sv_comp_overall_score()

    return cumulative_distance, 0
