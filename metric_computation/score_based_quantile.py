from typing import List

from csv_score_load_manager import CsvScoreItem


class SumAllPositiveScores:
    """
    S(f, t) is the sum of all positive scores
    obtained by f within time t on any bug.
    """
    def __init__(self, technique_csv_score_items: List[CsvScoreItem]):
        self._technique_csv_score_items = technique_csv_score_items

    def get_value(self, t_parameter: int) -> float:
        sum_all_pos_scores = 0

        for csv in self._technique_csv_score_items:
            # T(f ,b) <= t and
            # S(f, b) > 0
            experiment_time = csv.get_experiment_time_seconds()
            overall_score = csv.get_metric_our_val().get_sv_comp_overall_score()
            if experiment_time <= t_parameter and overall_score > 0:
                sum_all_pos_scores += overall_score

        return sum_all_pos_scores


class SumAllNegativeScores:
    """
    S_0(f) is the sum of all negative scores
    of fault localization technique f on any bug.
    """
    def __init__(self, technique_csv_score_items: List[CsvScoreItem]):
        self._technique_csv_score_items = technique_csv_score_items

    def get_value(self) -> float:
        sum_all_negative_scores = 0

        for csv in self._technique_csv_score_items:
            # S(f ,b) < 0
            overall_score = csv.get_metric_our_val().get_sv_comp_overall_score()
            if overall_score < 0:
                sum_all_negative_scores += overall_score

        return sum_all_negative_scores

