from typing import Dict, Tuple, List, Optional

import mathematics
from csv_score_load_manager import CsvScoreItem, FLTechnique, FLGranularity
from entity_type import ScoredStatement
from score_reassignment import assign_new_scores_to_list_statement


class AverageFaultLocalization:
    def __init__(self,
                 all_csv_score_items: List[CsvScoreItem],
                 include_all_technique_scores: bool):
        for item in all_csv_score_items:
            assert item.get_bug_key() == all_csv_score_items[0].get_bug_key()
        self._all_csv_score_items = all_csv_score_items
        self._include_all_technique_scores = include_all_technique_scores
        self._is_mutable = all_csv_score_items[0].get_is_mutable_bug()
        self._is_predicate = all_csv_score_items[0].get_is_predicate()
        self._is_crashing = all_csv_score_items[0].get_is_crashing()
        self._bug_number = all_csv_score_items[0].get_bug_number()
        self._project_name = all_csv_score_items[0].get_project_name()
        self._percentage_of_mutants_on_ground_truth = all_csv_score_items[0].get_percentage_of_mutants_on_ground_truth()
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

        normalized_score = mathematics.get_normalized_value(min_value, max_value, score_value)
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
                current_statement_normalized_scores.append((csv_score_item.get_technique(), current_normalized_score))
            average_score = self._get_average_score(current_statement_normalized_scores)
            statement_name_parts = statement_name.split("::")
            file_name = statement_name_parts[0]
            line_number = int(statement_name_parts[1])
            current_scored_statement = ScoredStatement(file_name, average_score, line_number)
            scored_statement_list.append(current_scored_statement)

        # reassigned_score_statement_list = assign_new_scores_to_list_statement(scored_statement_list)

        scored_statement_list.sort(key=lambda x: x.get_score(), reverse=True)
        csv_score_item = CsvScoreItem(None,
                                      None,
                                      self._project_name,
                                      self._bug_number,
                                      FLTechnique.Average,
                                      FLGranularity.Statement,
                                      scored_statement_list,
                                      -1)
        csv_score_item.set_is_crashing(self._is_crashing)
        csv_score_item.set_is_predicate(self._is_predicate)
        csv_score_item.set_is_mutable_bug(self._is_mutable)
        csv_score_item.set_percentage_of_mutants_on_ground_truth(
            self._percentage_of_mutants_on_ground_truth)

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
    def _get_average_score(technique_score_list: List[Tuple[FLTechnique, Optional[float]]]) -> float:
        ochiai_w = 1
        dstar_w = 1
        # metallaxis_w = 1
        # ps_w = 1.5
        st_w = 2

        w_sum = 0
        for item in technique_score_list:
            technique_score = item[1]
            if technique_score is None:
                technique_score = 0
            if item[0] == FLTechnique.Ochiai:
                w_sum += ochiai_w * technique_score
            elif item[0] == FLTechnique.DStar:
                w_sum += dstar_w * technique_score
            # elif item[0] == FLTechnique.Metallaxis:
            #     w_sum += metallaxis_w * technique_score
            # elif item[0] == FLTechnique.Muse:
            #     w_sum += muse_w * technique_score
            # elif item[0] == FLTechnique.PS:
            #     w_sum += ps_w * technique_score
            elif item[0] == FLTechnique.ST:
                w_sum += st_w * technique_score
            else:
                raise Exception("This one should not happen")

        average_score = w_sum / len(technique_score_list)

        return average_score
