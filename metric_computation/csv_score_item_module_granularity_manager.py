import copy
from typing import List

from csv_score_load_manager import CsvScoreItem, FLGranularity
from entity_type import ScoredStatement, ScoredModule


class CsvScoreItemModuleGranularityManager:
    def __init__(self,
                 statement_csv_score_items: List[CsvScoreItem]):
        self._statement_csv_score_items = statement_csv_score_items

    def get_module_csv_score_items(self):
        csv_module_list = []
        for csv_statement in self._statement_csv_score_items:
            current_csv_module = self._csv_statement_to_module(csv_statement)
            csv_module_list.append(current_csv_module)

        return csv_module_list

    def _csv_statement_to_module(self, csv_statement: CsvScoreItem) -> CsvScoreItem:
        scored_statement_list = csv_statement.get_scored_entities()
        assert len(scored_statement_list) == 0 or any([isinstance(x, ScoredStatement) for x in scored_statement_list])

        scored_module_list = self._scored_statement_list_to_scored_module_list(scored_statement_list)

        current_csv_module = copy.copy(csv_statement)
        current_csv_module.set_csv_paths(None)
        current_csv_module.set_script_id(None)
        current_csv_module.set_experiment_time_seconds(-1)
        current_csv_module.set_granularity(FLGranularity.Module)
        current_csv_module.set_scored_entities(scored_module_list)

        return current_csv_module

    @staticmethod
    def _scored_statement_list_to_scored_module_list(scored_statement_list: List[ScoredStatement]) -> List[ScoredModule]:
        module_full_name_score_dict = {}
        for item in scored_statement_list:
            module_full_name = item.get_file_path()
            current_statement_score = item.get_score()
            if module_full_name in module_full_name_score_dict.keys():
                previous_module_score = module_full_name_score_dict[module_full_name]
                new_module_score = max(previous_module_score, current_statement_score)
                module_full_name_score_dict[module_full_name] = new_module_score
            else:
                module_full_name_score_dict[module_full_name] = current_statement_score

        scored_module_list = []
        for key, value in module_full_name_score_dict.items():
            new_scored_module = ScoredModule(key, value)
            scored_module_list.append(new_scored_module)

        scored_module_list.sort(key=lambda x: x.get_score(), reverse=True)

        return scored_module_list


