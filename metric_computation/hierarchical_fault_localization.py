from typing import List, Tuple

from csv_score_load_manager import CsvScoreItem, FLGranularity
from entity_type import ScoredStatement
from hierarchical_types import ModuleRecord, FunctionRecord
from score_reassignment import assign_new_scores_to_list_statement


class HierarchicalFaultLocalization:
    def __init__(self,
                 statement_csv_score_item: CsvScoreItem,
                 function_csv_score_item: CsvScoreItem,
                 module_csv_score_item: CsvScoreItem):
        self._statement_csv_score_item = statement_csv_score_item
        self._function_csv_score_item = function_csv_score_item
        self._module_csv_score_item = module_csv_score_item
        assert (statement_csv_score_item.get_bug_key() ==
                function_csv_score_item.get_bug_key() ==
                module_csv_score_item.get_bug_key())

    def get_mfs_hfl_statement_csv_score_item(self) -> CsvScoreItem:
        mfs_scored_statement_list = self._get_mfs_scored_statement_list()
        current_csv_statement = self._get_csv_scored_item_for_scored_statement_list(mfs_scored_statement_list)

        return current_csv_statement

    def get_fs_hfl_statement_csv_score_item(self) -> CsvScoreItem:
        fs_scored_statement_list = self._get_fs_scored_statement_list()
        current_csv_statement = self._get_csv_scored_item_for_scored_statement_list(fs_scored_statement_list)

        return current_csv_statement

    def _get_mfs_scored_statement_list(self) -> List[ScoredStatement]:
        scored_statement_list = []
        module_record_list = self._get_module_record_list()
        for module_record in module_record_list:
            scored_statement_list += module_record.get_scored_statement_list()

        return scored_statement_list

    def _get_fs_scored_statement_list(self) -> List[ScoredStatement]:
        scored_statement_list = []
        function_record_list = self._get_function_record_list()
        for function_record in function_record_list:
            for scored_statement in function_record.get_scored_statement_list():
                if scored_statement not in scored_statement_list:
                    scored_statement_list.append(scored_statement)

        return scored_statement_list

    def _get_module_record_list(self) -> List[ModuleRecord]:
        module_record_list = []
        for scored_module in self._module_csv_score_item.get_scored_entities():
            function_record_list = self._get_function_record_list_in_module(scored_module.get_file_path())
            module_record = ModuleRecord(function_record_list,
                                         scored_module.get_file_path(),
                                         scored_module.get_score())
            module_record_list.append(module_record)

        return module_record_list

    def _get_function_record_list_in_module(self, file_path: str) -> List[FunctionRecord]:
        function_record_list = []
        for scored_function in self._function_csv_score_item.get_scored_entities():
            if scored_function.get_file_path() == file_path:
                scored_statement_list = self._get_scored_statement_list_in_function(scored_function.get_file_path(),
                                                                                    scored_function.get_function_range())
                function_record = FunctionRecord(scored_statement_list,
                                                 scored_function.get_file_path(),
                                                 scored_function.get_score(),
                                                 scored_function.get_function_range(),
                                                 scored_function.get_function_name())
                function_record_list.append(function_record)

        return function_record_list

    def _get_function_record_list(self) -> List[FunctionRecord]:
        function_record_list = []
        for scored_function in self._function_csv_score_item.get_scored_entities():
            scored_statement_list = self._get_scored_statement_list_in_function(scored_function.get_file_path(),
                                                                                scored_function.get_function_range())
            function_record = FunctionRecord(scored_statement_list,
                                             scored_function.get_file_path(),
                                             scored_function.get_score(),
                                             scored_function.get_function_range(),
                                             scored_function.get_function_name())
            function_record_list.append(function_record)

        return function_record_list

    def _get_scored_statement_list_in_function(self,
                                               file_path: str,
                                               function_range: Tuple[int, int]) -> List[ScoredStatement]:
        scored_statement_list = []
        for scored_statement in self._statement_csv_score_item.get_scored_entities():
            if (scored_statement.get_file_path() == file_path and
                    function_range[0] <= scored_statement.get_line_number() <= function_range[1]):
                scored_statement_list.append(scored_statement)

        return scored_statement_list

    def _get_csv_scored_item_for_scored_statement_list(self, new_scored_statement_list):
        # TODO: Check if == can replace >=.
        assert len(self._statement_csv_score_item.get_scored_entities()) >= len(new_scored_statement_list)
        reassigned_new_scored_statement_list = assign_new_scores_to_list_statement(new_scored_statement_list)
        assert len(new_scored_statement_list) == len(reassigned_new_scored_statement_list)

        project_name = self._statement_csv_score_item.get_project_name()
        bug_number = self._statement_csv_score_item.get_bug_number()
        localization_technique = self._statement_csv_score_item.get_technique()
        current_csv_statement = CsvScoreItem(None,
                                             None,
                                             project_name,
                                             bug_number,
                                             localization_technique,
                                             FLGranularity.Statement,
                                             reassigned_new_scored_statement_list,
                                             -1)
        current_csv_statement.set_is_crashing(self._statement_csv_score_item.get_is_crashing())
        current_csv_statement.set_is_predicate(self._statement_csv_score_item.get_is_predicate())

        return current_csv_statement
