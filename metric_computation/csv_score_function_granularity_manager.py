import copy
from pathlib import Path
from typing import List

from csv_score_load_manager import CsvScoreItem, FLGranularity
from entity_type import ScoredStatement, ScoredFunction
from function_manager import FunctionManager, StatementFunctionMap


class CsvScoreItemFunctionGranularityManager:

    def __init__(self,
                 statement_csv_score_items: List[CsvScoreItem],
                 workspace_path: Path):
        self._statement_csv_score_items = statement_csv_score_items
        self._workspace_path = workspace_path

    def get_function_csv_score_items(self) -> List[CsvScoreItem]:
        csv_function_list = []
        for csv_statement in self._statement_csv_score_items:
            current_csv_func = self._csv_statement_to_function(csv_statement)
            csv_function_list.append(current_csv_func)

        return csv_function_list

    def _csv_statement_to_function(self, csv_statement: CsvScoreItem) -> CsvScoreItem:
        scored_statement_list = csv_statement.get_scored_entities()
        assert len(scored_statement_list) == 0 or any([isinstance(x, ScoredStatement) for x in scored_statement_list])
        statement_list = [(x.get_file_path(), x.get_line_number()) for x in scored_statement_list]

        function_manager = FunctionManager(self._workspace_path,
                                           csv_statement.get_project_name(),
                                           csv_statement.get_bug_number())
        statement_to_function_map = function_manager.get_statement_to_function_map(statement_list)

        scored_function_list = self._map_scored_statement_list_to_scored_function_list(statement_to_function_map, scored_statement_list)

        current_csv_function = copy.copy(csv_statement)
        current_csv_function.set_csv_paths(None)
        current_csv_function.set_script_id(None)
        current_csv_function.set_granularity(FLGranularity.Function)
        current_csv_function.set_scored_entities(scored_function_list)

        return current_csv_function

    @staticmethod
    def _map_scored_statement_list_to_scored_function_list(statement_to_function_map: StatementFunctionMap,
                                                           scored_statements: List[ScoredStatement]) -> List[ScoredFunction]:
        # Paper "An Empirical Study of Fault Localization Families
        # and Their Combinations" (Section 4.5 in paper):
        # "The suspiciousness score for a method is defined
        # as the maximum score of its statements."
        # We also do the same thing.

        function_score_dict = {}
        for item in scored_statements:
            current_function_info = statement_to_function_map.get_function_info(item.get_file_path(),
                                                                                item.get_line_number())
            if current_function_info is not None:
                if str(current_function_info) in function_score_dict.keys():
                    prev_score, prev_func_info = function_score_dict[str(current_function_info)]
                    function_score_dict[str(current_function_info)] = max(prev_score, item.get_score()), prev_func_info
                else:
                    function_score_dict[str(current_function_info)] = item.get_score(), current_function_info

        scored_function_list = []
        for item in function_score_dict.values():
            item_score = item[0]
            item_function_info = item[1]
            current_scored_function = ScoredFunction(item_function_info.get_module_path(),
                                                     item_score,
                                                     item_function_info.get_function_range(),
                                                     item_function_info.get_function_name())
            scored_function_list.append(current_scored_function)
            scored_function_list.sort(key=lambda x: x.get_score(), reverse=True)
        return scored_function_list
