from pathlib import Path
from typing import Dict, List, Tuple

from database_manager import MbflDatabaseManager, get_line_name


class MbflExperimentInfo:
    def __init__(self,
                 project_name: str,
                 bug_number: int,
                 is_mutable_bug: bool,
                 percentage_of_mutants_on_ground_truth: float):
        self._project_name = project_name
        self._bug_number = bug_number
        self._is_mutable_bug = is_mutable_bug
        self._percentage_of_mutants_on_ground_truth = percentage_of_mutants_on_ground_truth

    def _pretty_representation(self):
        return (f"{self._project_name} "
                f"{self._bug_number}")

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    def get_project_name(self) -> str:
        return self._project_name

    def get_bug_number(self) -> int:
        return self._bug_number

    def is_mutable_bug(self) -> bool:
        return self._is_mutable_bug

    def get_percentage_of_mutants_on_ground_truth(self) -> float:
        return self._percentage_of_mutants_on_ground_truth

    def get_bug_key(self) -> str:
        return _get_bug_key(self.get_project_name(), self.get_bug_number())


def _get_bug_key(project_name: str, bug_number: int) -> str:
    return f"{project_name}:{bug_number}"


class MutableBugsAnalysis:
    def __init__(self, results_path: Path, ground_truth_info: Dict):
        self._results_path = results_path
        self._ground_truth_info = ground_truth_info
        self._mbfl_experiment_info_list = self._load_mbfl_experiment_info_list()

    def get_mutable_bug_keys(self) -> List[str]:
        mutable_bug_keys = [x.get_bug_key() for x in self._mbfl_experiment_info_list if x.is_mutable_bug()]
        return mutable_bug_keys

    def get_percentage_of_mutants_on_ground_truth(self) -> Dict[str, float]:
        percentage_dict = {}
        for mbfl_experiment_info in self._mbfl_experiment_info_list:
            percentage_dict[mbfl_experiment_info.get_bug_key()] = mbfl_experiment_info.get_percentage_of_mutants_on_ground_truth()

        return percentage_dict

    def _load_mbfl_experiment_info_list(self) -> List[MbflExperimentInfo]:
        mbfl_dirs = [x for x in self._results_path.iterdir() if "mbfl" in x.name]
        mbfl_experiment_info_list = []
        for mbfl_dir in mbfl_dirs:
            current_mbfl_experiment_info = self._get_mbfl_experiment_info(mbfl_dir)
            mbfl_experiment_info_list.append(current_mbfl_experiment_info)

        mbfl_experiment_info_list.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))
        return mbfl_experiment_info_list

    def _get_mbfl_experiment_info(self, mbfl_dir) -> MbflExperimentInfo:
        name_parts = mbfl_dir.name.split("_")
        assert name_parts[5] == "mbfl"
        assert name_parts[6] == "statement"
        project_name = name_parts[3]
        bug_number = int(name_parts[4])

        num_ground_truth_info_mutated_correctly, percentage = self._get_num_ground_truth_info_mutated_correctly(
            mbfl_dir,
            project_name,
            bug_number)
        percentage_of_mutants_on_ground_truth = self._percentage_of_mutants_on_ground_truth(mbfl_dir,
                                                                                            project_name,
                                                                                            bug_number)

        is_mutable_bug = num_ground_truth_info_mutated_correctly > 0

        mbfl_experiment_info = MbflExperimentInfo(project_name,
                                                  bug_number,
                                                  is_mutable_bug,
                                                  percentage_of_mutants_on_ground_truth)

        return mbfl_experiment_info

    def _get_num_ground_truth_info_mutated_correctly(self,
                                                     mbfl_dir: Path,
                                                     project_name: str,
                                                     bug_number: int) -> Tuple[int, int]:
        db_path = self._get_db_path(mbfl_dir)
        mbfl_db_manager = MbflDatabaseManager(db_path)

        mutation_line_list = mbfl_db_manager.get_correct_mutation_line_list()
        ground_truth_line_list = self._get_ground_truth_line_list(project_name, bug_number)

        correctly_mutated_ground_truth_line_set = set()
        for ground_truth_line in ground_truth_line_list:
            if ground_truth_line in mutation_line_list:
                correctly_mutated_ground_truth_line_set.add(ground_truth_line)

        correctly_mutated_ground_truth_line_set = list(correctly_mutated_ground_truth_line_set)
        percentage = round(len(correctly_mutated_ground_truth_line_set) / len(ground_truth_line_list) * 100)
        return len(correctly_mutated_ground_truth_line_set), percentage

    def _percentage_of_mutants_on_ground_truth(self,
                                               mbfl_dir: Path,
                                               project_name: str,
                                               bug_number: int) -> float:
        db_path = self._get_db_path(mbfl_dir)
        mbfl_db_manager = MbflDatabaseManager(db_path)

        mutant_info_list = mbfl_db_manager.get_correct_mutant_info_list()
        ground_truth_line_list = self._get_ground_truth_line_list(project_name, bug_number)

        count = 0
        for mutant_id, mutant_lines in mutant_info_list.items():
            for mutant_line in mutant_lines:
                if mutant_line in ground_truth_line_list:
                    count += 1
                    break

        if len(mutant_info_list) == 0:
            percentage = 0
        else:
            percentage = (count / len(mutant_info_list)) * 100

        return percentage

    def _get_ground_truth_line_list(self,
                                    project_name: str,
                                    bug_number: int):
        bug_key = _get_bug_key(project_name, bug_number)
        project_ground_truth_info = self._ground_truth_info[bug_key]

        ground_truth_line_set = set()
        for module_ground_truth_item in project_ground_truth_info:
            module_path = module_ground_truth_item["FILE_NAME"]
            line_list = module_ground_truth_item["LINES"]
            extended_line_list = module_ground_truth_item["EXTENDED_LINES"]
            all_line_list = line_list + extended_line_list
            for line_num in all_line_list:
                current_line_name = get_line_name(module_path, line_num)
                ground_truth_line_set.add(current_line_name)

        ground_truth_line_list = list(ground_truth_line_set)
        ground_truth_line_list.sort()
        return ground_truth_line_list

    @staticmethod
    def _get_db_path(mbfl_dir: Path) -> Path:
        dirs_in_mbfl_dir = [x for x in mbfl_dir.iterdir() if x.is_dir()]
        assert len(dirs_in_mbfl_dir) == 1
        db_path = dirs_in_mbfl_dir[0] / "fauxpy.db"
        return db_path


