import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict


def get_line_name(module_path: str, line_num: int) -> str:
    return f"{module_path}::{line_num}"


class MbflDatabaseManager:
    Mutant_info_table_name = "MutantInfo"
    Failing_line_number_table_name = "FailingLineNumber"

    def __init__(self, db_path: Path):
        self._db_path = db_path

    def get_correct_mutation_line_list(self) -> List[str]:
        rows = self._get_mutant_info_table()

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

    @staticmethod
    def _get_generalized_module_path(module_path: str) -> str:
        element_parts = module_path.split("/")
        generalized_module_path = "/".join(element_parts[6:])

        return generalized_module_path

    def get_correct_mutant_info_list(self) -> Dict[str, List[str]]:
        correct_mutant_info_dict = {}
        rows = self._get_mutant_info_table()
        for row in rows:
            time_out = row[3]
            has_missing_tests = row[4]
            if time_out == -1 and has_missing_tests == -1:
                module_path = self._get_generalized_module_path(row[0])
                start_pos = row[1]
                end_pos = row[2]
                mutant_id = row[5]
                current_mutant_line_list = []
                for line_item in range(start_pos, end_pos + 1):
                    current_line_name = get_line_name(module_path, line_item)
                    current_mutant_line_list.append(current_line_name)
                correct_mutant_info_dict[mutant_id] = current_mutant_line_list

        return correct_mutant_info_dict

    def _get_mutant_info_table(self) -> List[Tuple]:
        with sqlite3.connect(self._db_path) as con:
            cur = con.cursor()
            cur.execute(f"SELECT ModulePath, "
                        f"StartPos, "
                        f"EndPos, "
                        f"TimeOut, "
                        f"HasMissingTests,"
                        f"MutantId "
                        f"FROM {self.Mutant_info_table_name}")
            rows = cur.fetchall()

        return rows


class PsDatabaseManager:
    Candidate_predicate_table_name = "PredicateSequence"

    def __init__(self, db_path: Path):
        self._db_path = db_path

    def get_number_of_predicate_instances(self) -> Tuple[int, int]:
        with sqlite3.connect(self._db_path) as con:
            cur = con.cursor()
            cur.execute(f"SELECT TestName, "
                        f"IndexedPredicateSequence "
                        f"FROM {self.Candidate_predicate_table_name}")
            rows = cur.fetchall()

        number_of_failing_tests = len(rows)
        num_predicate_instance = 0
        for indexed_predicate_sequence in rows:
            current_sequence = indexed_predicate_sequence[1]
            predicates_in_seq = current_sequence.split(",")
            num_predicate_instance += len(predicates_in_seq)

        return num_predicate_instance, number_of_failing_tests
