from typing import List

from csv_score_load_manager import CsvScoreItem


class CsvScoreItemFunctionGranularityManager:

    def __init__(self, statement_csv_score_items: List[CsvScoreItem]):
        self._statement_csv_score_items = statement_csv_score_items

    def get_function_csv_score_items(self):
        pass
