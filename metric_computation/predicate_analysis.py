from pathlib import Path
from typing import Dict, Tuple

from database_manager import PsDatabaseManager


class PredicateAnalysis:
    def __init__(self, results_path: Path):
        self._results_path = results_path

    def get_number_of_predicate_instances_dict(self) -> Dict[str, Tuple[int, int]]:
        number_of_predicate_instances_dict = {}
        ps_dirs = [x for x in self._results_path.iterdir() if "_ps" in x.name]

        for dir_item in ps_dirs:
            current_bug_key = self._get_bug_key(dir_item)
            (current_number_of_predicate_instances,
             current_number_of_failing_tests) = self.get_number_of_predicate_instances_and_failing_tests(dir_item)
            number_of_predicate_instances_dict[current_bug_key] = (current_number_of_predicate_instances,
                                                                   current_number_of_failing_tests)

        return number_of_predicate_instances_dict

    @staticmethod
    def _get_bug_key(dir_item: Path) -> str:
        path_parts = dir_item.name.split("_")
        project_name = path_parts[3]
        bug_number = int(path_parts[4])

        bug_key = f"{project_name}:{bug_number}"

        return bug_key

    def get_number_of_predicate_instances_and_failing_tests(self, dir_item: Path) -> Tuple[int, int]:
        db_path = self._get_db_path(dir_item)
        ps_database_manager = PsDatabaseManager(db_path)
        (number_of_predicate_instances,
         number_of_failing_tests) = ps_database_manager.get_number_of_predicate_instances()

        return number_of_predicate_instances, number_of_failing_tests

    @staticmethod
    def _get_db_path(ps_dir: Path) -> Path:
        dirs_in_ps_dirs = [x for x in ps_dir.iterdir() if x.is_dir()]
        assert len(dirs_in_ps_dirs) == 1
        db_path = dirs_in_ps_dirs[0] / "fauxpy.db"
        return db_path
