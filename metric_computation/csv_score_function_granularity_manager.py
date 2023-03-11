from pathlib import Path
from typing import List

from csv_score_load_manager import CsvScoreItem


class CsvScoreItemFunctionGranularityManager:

    def __init__(self,
                 statement_csv_score_items: List[CsvScoreItem],
                 workspace_path: Path):
        self._statement_csv_score_items = statement_csv_score_items
        self._workspace_path = workspace_path

    def get_function_csv_score_items(self):
        pass
