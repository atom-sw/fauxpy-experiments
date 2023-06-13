from typing import Dict, Tuple, List, Optional

import mathematics
from csv_score_load_manager import CsvScoreItem, FLTechnique, FLGranularity
from entity_type import ScoredStatement, ScoredEntity, ScoredFunction, ScoredModule


class AverageFaultLocalization:
    def __init__(self, all_csv_score_items: List[CsvScoreItem], avg_technique: FLTechnique):
        for item in all_csv_score_items:
            assert item.get_bug_key() == all_csv_score_items[0].get_bug_key()
            assert item.get_granularity() == all_csv_score_items[0].get_granularity()
        assert avg_technique == FLTechnique.AvgAlfa or avg_technique == FLTechnique.AvgSbst
        assert ((len(all_csv_score_items) == 6 and avg_technique == FLTechnique.AvgAlfa) or
                (len(all_csv_score_items) == 3 and avg_technique == FLTechnique.AvgSbst))
        self._granularity = all_csv_score_items[0].get_granularity()
        self._all_csv_score_items = all_csv_score_items
        self._is_mutable = all_csv_score_items[0].get_is_mutable_bug()
        self._is_predicate = all_csv_score_items[0].get_is_predicate()
        self._is_crashing = all_csv_score_items[0].get_is_crashing()
        self._bug_number = all_csv_score_items[0].get_bug_number()
        self._project_name = all_csv_score_items[0].get_project_name()
        self._percentage_of_mutants_on_ground_truth = all_csv_score_items[0].get_percentage_of_mutants_on_ground_truth()
        self._technique_min_max = self._get_technique_min_max()
        self._avg_technique = avg_technique

    def _get_technique_min_max(self) -> Dict[FLTechnique, Tuple[float, float]]:
        def get_min_max(scored_entities: List[ScoredEntity]) -> Tuple[Optional[float], Optional[float]]:
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

    def get_average_fl_csv_score_item(self) -> CsvScoreItem:
        scored_entity_list = []

        all_entity_names = self._get_all_scored_entities()
        for entity_name in all_entity_names:
            current_entity_normalized_scores = []
            for csv_score_item in self._all_csv_score_items:
                current_technique_score = self._get_entity_score_for_technique(entity_name, csv_score_item)
                current_normalized_score = self._get_normalized_scored_for_technique(current_technique_score,
                                                                                     csv_score_item.get_technique())
                current_entity_normalized_scores.append((csv_score_item.get_technique(), current_normalized_score))
            average_score = self._get_average_score(current_entity_normalized_scores)

            current_scored_entity = self._get_scored_entity_from_name(entity_name, average_score)
            scored_entity_list.append(current_scored_entity)

        scored_entity_list.sort(key=lambda x: x.get_score(), reverse=True)
        csv_score_item = CsvScoreItem(None,
                                      None,
                                      self._project_name,
                                      self._bug_number,
                                      self._avg_technique,
                                      self._granularity,
                                      scored_entity_list,
                                      -1)
        csv_score_item.set_is_crashing(self._is_crashing)
        csv_score_item.set_is_predicate(self._is_predicate)
        csv_score_item.set_is_mutable_bug(self._is_mutable)
        csv_score_item.set_percentage_of_mutants_on_ground_truth(
            self._percentage_of_mutants_on_ground_truth)

        return csv_score_item

    def _get_all_scored_entities(self) -> List[str]:
        all_entities = []
        for csv_score_item in self._all_csv_score_items:
            for scored_entities in csv_score_item.get_scored_entities():
                if scored_entities.get_entity_name() not in all_entities:
                    all_entities.append(scored_entities.get_entity_name())
        return all_entities

    @staticmethod
    def _get_entity_score_for_technique(entity_name: str,
                                        csv_score_item: CsvScoreItem) -> Optional[float]:
        for scored_entity in csv_score_item.get_scored_entities():
            if scored_entity.get_entity_name() == entity_name:
                return scored_entity.get_score()

        return None

    def _get_average_score(self, technique_score_list: List[Tuple[FLTechnique, Optional[float]]]) -> float:
        ochiai_w = 3
        dstar_w = 3
        metallaxis_w = 2
        muse_w = 2
        ps_w = 1
        st_w = 1

        w_sum = 0
        for item in technique_score_list:
            technique_score = item[1]
            if technique_score is None:
                technique_score = 0
            if item[0] == FLTechnique.Ochiai:
                w_sum += ochiai_w * technique_score
            elif item[0] == FLTechnique.DStar:
                w_sum += dstar_w * technique_score
            elif item[0] == FLTechnique.Metallaxis:
                w_sum += metallaxis_w * technique_score
            elif item[0] == FLTechnique.Muse:
                w_sum += muse_w * technique_score
            elif item[0] == FLTechnique.PS:
                w_sum += ps_w * technique_score
            elif item[0] == FLTechnique.ST:
                w_sum += st_w * technique_score
            else:
                raise Exception("This one should not happen")

        denominator = ochiai_w + dstar_w + st_w
        if self._avg_technique == FLTechnique.AvgAlfa:
            denominator += metallaxis_w + muse_w + ps_w

        average_score = w_sum / denominator

        return average_score

    def _get_scored_entity_from_name(self, entity_name, average_score) -> ScoredEntity:
        entity_name_parts = entity_name.split("::")
        if self._granularity == FLGranularity.Statement:
            file_name = entity_name_parts[0]
            line_number = int(entity_name_parts[1])
            current_scored_entity = ScoredStatement(file_name, average_score, line_number)
        elif self._granularity == FLGranularity.Function:
            # black.py::patch_click::6320::6339
            file_name = entity_name_parts[0]
            func_name = entity_name_parts[1]
            func_range = (int(entity_name_parts[2]), int(entity_name_parts[3]))
            current_scored_entity = ScoredFunction(file_name, average_score, func_range, func_name)
        elif self._granularity == FLGranularity.Module:
            current_scored_entity = ScoredModule(entity_name, average_score)
        else:
            raise Exception()

        return current_scored_entity
