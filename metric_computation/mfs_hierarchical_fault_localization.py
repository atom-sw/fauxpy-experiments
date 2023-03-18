from csv_score_load_manager import CsvScoreItem


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

    def get_mfs_hfl_statement_csv_score_item(self):
        pass

