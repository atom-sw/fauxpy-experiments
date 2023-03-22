from typing import Dict, Tuple, List, Optional

import mathematics
from csv_score_load_manager import CsvScoreItem, FLTechnique, FLGranularity
from entity_type import ScoredStatement
from score_reassignment import assign_new_scores_to_list_statement


class AverageFaultLocalization:
    def __init__(self,
                 ochiai_csv: CsvScoreItem,
                 metallaxis_csv: CsvScoreItem,
                 muse_csv: CsvScoreItem,
                 ps_csv: CsvScoreItem,
                 st_csv: CsvScoreItem):
        self._ochiai_csv = ochiai_csv
        self._metallaxis_csv = metallaxis_csv
        self._muse_csv = muse_csv
        self._ps_csv = ps_csv
        self._st_csv = st_csv
        assert (ochiai_csv.get_bug_key() ==
                metallaxis_csv.get_bug_key() ==
                muse_csv.get_bug_key() ==
                ps_csv.get_bug_key() ==
                st_csv.get_bug_key())
        self._all_csv_score_items = [self._ochiai_csv,
                                     self._metallaxis_csv,
                                     self._muse_csv,
                                     self._ps_csv,
                                     self._st_csv]
        self._technique_min_max = self._get_technique_min_max()

    def _get_technique_min_max(self) -> Dict[FLTechnique, Tuple[float, float]]:
        def get_min_max(scored_entities: List[ScoredStatement]) -> Tuple[Optional[float], Optional[float]]:
            all_scores = [x.get_score() for x in scored_entities]
            if len(all_scores) == 0:
                return None, None

            min_val = min(all_scores)
            max_val = max(all_scores)
            return min_val, max_val

        technique_min_max = {}
        for csv_score_item in self._all_csv_score_items:
            technique = csv_score_item.get_technique()
            min_value, max_value = get_min_max(csv_score_item.get_scored_entities())
            technique_min_max[technique] = (min_value, max_value)

        return technique_min_max

    def _get_normalized_scored_for_technique(self,
                                             score_value: Optional[float],
                                             technique: FLTechnique) -> Optional[float]:
        if score_value is None:
            return None

        min_value, max_value = self._technique_min_max[technique]

        if min_value == max_value:
            if score_value == 0:
                return 0
            else:
                return 1

        normalized_score = (score_value - min_value) / (max_value - min_value)
        return normalized_score

    def get_average_fl_statement_csv_score_item(self) -> CsvScoreItem:
        scored_statement_list = []

        all_statement_names = self._get_all_scored_statements()
        for statement_name in all_statement_names:
            current_statement_normalized_scores = []
            for csv_score_item in self._all_csv_score_items:
                current_technique_score = self._get_statement_score_for_technique(statement_name, csv_score_item)
                current_normalized_score = self._get_normalized_scored_for_technique(current_technique_score,
                                                                                     csv_score_item.get_technique())
                current_statement_normalized_scores.append(current_normalized_score)
            average_score = self._get_average_score(current_statement_normalized_scores)
            statement_name_parts = statement_name.split("::")
            file_name = statement_name_parts[0]
            line_number = int(statement_name_parts[1])
            current_scored_statement = ScoredStatement(file_name, average_score, line_number)
            scored_statement_list.append(current_scored_statement)

        reassigned_score_statement_list = assign_new_scores_to_list_statement(scored_statement_list)

        csv_score_item = CsvScoreItem(None,
                                      None,
                                      self._ochiai_csv.get_project_name(),
                                      self._ochiai_csv.get_bug_number(),
                                      FLTechnique.Average,
                                      FLGranularity.Statement,
                                      reassigned_score_statement_list,
                                      -1)
        csv_score_item.set_is_crashing(self._ochiai_csv.get_is_crashing())
        csv_score_item.set_is_predicate(self._ochiai_csv.get_is_predicate())

        return csv_score_item

    def _get_all_scored_statements(self) -> List[str]:
        all_statements = []
        for csv_score_item in self._all_csv_score_items:
            for scored_statement in csv_score_item.get_scored_entities():
                if scored_statement.get_entity_name() not in all_statements:
                    all_statements.append(scored_statement.get_entity_name())
        return all_statements

    @staticmethod
    def _get_statement_score_for_technique(statement_name: str,
                                           csv_score_item: CsvScoreItem) -> Optional[float]:
        for scored_statement in csv_score_item.get_scored_entities():
            if scored_statement.get_entity_name() == statement_name:
                return scored_statement.get_score()

        return None

    @staticmethod
    def _get_average_score(scores: List[Optional[float]]) -> float:
        non_none_score_list = list(filter(lambda x: x is not None, scores))
        assert len(non_none_score_list) > 0
        average_score = mathematics.average(non_none_score_list)
        return average_score
