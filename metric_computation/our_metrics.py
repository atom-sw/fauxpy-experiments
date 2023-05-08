import math
from typing import List, Dict, Tuple

from csv_score_load_manager import CsvScoreItem, FLTechnique
from cumulative_distance import DistanceToBug, TechniqueBugCumulativeDistance
from entity_type import ScoredStatement
from score_based_quantile import SumAllPositiveScores
from sv_comp_score import SvCompScoreForBug, TechniqueBugSvCompOverallScore

"""
We use ScoredStatement class as program location.
A program location L_k is a triple <p_k, m_k, l_k>, where p_k is
the location’s package (corresponding to a directory within
the project), m_k is the location’s module (corresponding to a
file in p_k), and l_k is the location’s
line number (within m_k).
"""


def get_cumulative_distance(program_locations: List[ScoredStatement],
                            buggy_line_names: List[str],
                            buggy_module_sizes: Dict[str, int],
                            e_inspect: float):
    distance_to_bug_obj = DistanceToBug(buggy_line_names, buggy_module_sizes)
    technique_bug_cumulative_distance_obj = TechniqueBugCumulativeDistance(distance_to_bug_obj,
                                                                           program_locations,
                                                                           e_inspect)
    cumulative_distance = technique_bug_cumulative_distance_obj.get_cumulative_distance()

    return cumulative_distance


def get_sv_comp_overall_score(program_locations: List[ScoredStatement],
                              buggy_line_names: List[str],
                              buggy_module_sizes: Dict[str, int],
                              e_inspect: float):
    sv_comp_score_bug_obj = SvCompScoreForBug(buggy_line_names, buggy_module_sizes)
    technique_bug_sv_comp_overall_score_obj = TechniqueBugSvCompOverallScore(sv_comp_score_bug_obj,
                                                                             program_locations,
                                                                             e_inspect)
    sv_comp_overall_score = technique_bug_sv_comp_overall_score_obj.get_sv_comp_overall_score()

    return sv_comp_overall_score


class QuantileRecord:
    """
    Columns t, f, S(f, t)
    """

    def __init__(self, time_sec: int,
                 technique: FLTechnique,
                 sum_all_positive_scores: float):
        self._time_sec = time_sec
        self._technique = technique
        self._sum_all_positive_scores = sum_all_positive_scores

    def _pretty_representation(self):
        return f"{self._time_sec}, {self._technique.name}, {self._sum_all_positive_scores}"

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    def get_record(self) -> Tuple[float, str, float]:
        return self._time_sec, self._technique.name, self._sum_all_positive_scores


def score_based_quantile_function_for_technique(technique_csv_score_items: List[CsvScoreItem]) -> List[QuantileRecord]:
    first_csv_technique = technique_csv_score_items[0].get_technique()
    assert any([x.get_technique() == first_csv_technique for x in technique_csv_score_items])

    max_time_parameter = max([x.get_experiment_time_seconds() for x in technique_csv_score_items])

    sum_all_positive_scores_obj = SumAllPositiveScores(technique_csv_score_items)
    # sum_all_negative_scores_obj = SumAllNegativeScores(technique_csv_score_items)
    # sum_all_negative_scores = sum_all_negative_scores_obj.get_value()

    record_list = []
    for t_parameter in range(1, math.floor(max_time_parameter) + 1):
        sum_all_positive_scores_t = sum_all_positive_scores_obj.get_value(t_parameter)
        current_quantile_record = QuantileRecord(t_parameter, first_csv_technique, sum_all_positive_scores_t)
        record_list.append(current_quantile_record)

    return record_list
