from typing import List, Tuple

from entity_type import ScoredModule, ScoredFunction, ScoredStatement


class FunctionRecord(ScoredFunction):
    def __init__(self,
                 scored_statement_list: List[ScoredStatement],
                 file_path: str,
                 score: float,
                 function_range: Tuple[int, int],
                 function_name: str):
        super().__init__(file_path, score, function_range, function_name)
        self._scored_statement_list = scored_statement_list

    def get_scored_statement_list(self):
        return self._scored_statement_list


class ModuleRecord(ScoredModule):
    def __init__(self,
                 function_record_list: List[FunctionRecord],
                 file_path: str,
                 score: float):
        super().__init__(file_path, score)
        self._function_record_list = function_record_list

    def get_scored_statement_list(self) -> List[ScoredStatement]:
        scored_statement_list = []
        for function_record in self._function_record_list:
            current_scored_statement_list = function_record.get_scored_statement_list()
            for scored_statement in current_scored_statement_list:
                if scored_statement not in scored_statement_list:
                    scored_statement_list.append(scored_statement)

        return scored_statement_list
