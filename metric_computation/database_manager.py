import sqlite3
from pathlib import Path
from typing import List


def get_line_name(module_path: str, line_num: int) -> str:
    return f"{module_path}::{line_num}"


class MbflDatabaseManager:
    Mutant_info_table_name = "MutantInfo"
    Failing_line_number_table_name = "FailingLineNumber"

    def __init__(self, db_path: Path):
        self._db_path = db_path

    def get_correct_mutation_line_list(self) -> List[str]:
        with sqlite3.connect(self._db_path) as con:
            cur = con.cursor()
            cur.execute(f"SELECT ModulePath, "
                        f"StartPos, "
                        f"EndPos, "
                        f"TimeOut, "
                        f"HasMissingTests "
                        f"FROM {self.Mutant_info_table_name}")
            rows = cur.fetchall()

        correct_mutation_line_set = set()
        for row in rows:
            time_out = row[3]
            has_missing_tests = row[4]
            if time_out == -1 and has_missing_tests == -1:
                module_path = self._get_generalized_module_path(row[0])
                start_pos = row[1]
                end_pos = row[2]
                for line_item in range(start_pos, end_pos + 1):
                    current_line_name = get_line_name(module_path, line_item)
                    correct_mutation_line_set.add(current_line_name)

        correct_mutation_line_list = list(correct_mutation_line_set)
        correct_mutation_line_list.sort()
        return correct_mutation_line_list

    def get_failing_line_list(self) -> List[str]:
        with sqlite3.connect(self._db_path) as con:
            cur = con.cursor()
            cur.execute(f"SELECT ModulePath, "
                        f"LineNumber "
                        f"FROM {self.Failing_line_number_table_name}")
            rows = cur.fetchall()

        failing_line_set = set()
        for row in rows:
            module_path = self._get_generalized_module_path(row[0])
            line_number = row[1]
            current_line_name = get_line_name(module_path, line_number)
            failing_line_set.add(current_line_name)

        failing_line_list = list(failing_line_set)
        failing_line_list.sort()
        return failing_line_list

    @staticmethod
    def _get_generalized_module_path(module_path: str) -> str:
        element_parts = module_path.split("/")
        generalized_module_path = "/".join(element_parts[6:])

        return generalized_module_path
