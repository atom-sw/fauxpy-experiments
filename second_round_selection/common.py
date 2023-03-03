import csv
import json
import os.path
import shutil
from pathlib import Path
from typing import Any, List, Tuple

PATH_ITEMS_FILE_NAME = "path_items.json"
NO_SWAPPED_INSTANCES_SCORES_FILE_NAME = "Scores_fauxpy_no_swapped_instances.csv"
NO_CANDIDATE_PREDICATES_SCORES_FILE_NAME = "Scores_fauxpy_no_candidate_predicates.csv"
CORRECT_FISHY_CSV_FILE_NAME = "correct_fishy.csv"


class GarbageManager:
    GarbageDirName = "Garbage"

    def __init__(self, results_path: Path):
        self._results_path = results_path
        self._garbage_path = self._make_garbage_directory()

    def _make_garbage_directory(self):
        garbage_dir_path = self._results_path / GarbageManager.GarbageDirName
        if not garbage_dir_path.exists():
            garbage_dir_path.mkdir()
        return garbage_dir_path

    def move_to_garbage(self, item_path: Path):
        print("Moving to garbage ", item_path.name)
        shutil.move(item_path, self._garbage_path)


class PathManager:
    def __init__(self, path_items_file_path: str):
        self._path_items_file_path = path_items_file_path
        self._results_path, self._scripts_path = self.load_path_items()

    def load_path_items(self):
        results_path_object = load_json_to_dictionary(self._path_items_file_path)
        results_path = Path(results_path_object["RESULTS_PATH"])
        scripts_path = Path(results_path_object["SCRIPTS_PATH"])
        return results_path, scripts_path

    def get_results_path(self) -> Path:
        return self._results_path

    def get_scripts_path(self) -> Path:
        return self._scripts_path


class Item:
    def _load_info_from_script_name_part(self, script_name_part):
        name_parts = script_name_part.split("_")
        self._experiment_id = int(name_parts[0])
        self._timeout = int(name_parts[1][:-1])
        self._memory = int(name_parts[2][:-1])
        self._project_name = name_parts[3]
        self._bug_num = int(name_parts[4])
        self._family = name_parts[5]
        self._granularity = name_parts[6]

    def __str__(self):
        return self.pretty_representation()

    def __repr__(self):
        return self.pretty_representation()

    def __eq__(self, other):
        return self._experiment_id == other.get_experiment_id()

    def __ne__(self, other):
        return not self.__eq__(other)

    def pretty_representation(self):
        return (f"{self._experiment_id}, "
                f"{self._timeout}, "
                f"{self._memory}, "
                f"{self._project_name}, "
                f"{self._bug_num}, "
                f"{self._family}, "
                f"{self._granularity}")

    def get_experiment_id(self) -> int:
        return self._experiment_id

    def get_granularity(self) -> str:
        return self._granularity

    def get_timeout(self) -> int:
        return self._timeout

    def get_project_name(self):
        return self._project_name

    def get_bug_number(self):
        return self._bug_num


class ScriptItem(Item):
    def __init__(self, script_name: str):
        self._script_name = script_name

        script_name_part = self._script_name.split(".")[0]
        self._load_info_from_script_name_part(script_name_part)


class ResultItem(Item):
    def __init__(self, result_dir_path: Path):
        self._result_dir_path = result_dir_path
        self._is_correct_fishy = None

        script_name_part = "_".join(str(result_dir_path.name).split("_")[:-1])
        self._load_info_from_script_name_part(script_name_part)
        self._creation_time = os.path.getctime(str(result_dir_path.absolute().resolve()))

    def set_is_correct_fishy(self, value):
        self._is_correct_fishy = value

    def get_path(self):
        return self._result_dir_path

    def is_fishy(self):
        if self.is_corrupted() or self._is_correct_fishy:
            return False

        dir_paths = list(filter(lambda x: x.is_dir() and x, self._result_dir_path.iterdir()))
        assert len(dir_paths) == 1

        dir_path = dir_paths[0]
        dir_path_items = [x for x in dir_path.iterdir()]
        csv_items = list(filter(lambda x: x.name.endswith(".csv"), dir_path_items))
        if self._family == "sbfl":
            assert len(csv_items) == 3
            for csv_file in csv_items:
                if self._is_csv_fishy(csv_file):
                    return True
        elif self._family == "mbfl":
            assert len(csv_items) == 2
            metallaxis_file_csv = list(filter(lambda x: "Scores_Metallaxis.csv" in x.name, csv_items))[0]
            return self._is_csv_fishy(metallaxis_file_csv)
        elif self._family == "ps":
            assert len(csv_items) >= 1
            for csv_file in csv_items:
                if (csv_file.name != NO_SWAPPED_INSTANCES_SCORES_FILE_NAME and
                        csv_file.name != NO_CANDIDATE_PREDICATES_SCORES_FILE_NAME and
                        self._is_csv_fishy(csv_file)):
                    return True
        elif self._family == "st":
            assert len(csv_items) == 1
        else:
            raise Exception("This must not happen!")

        return False

    def is_corrupted(self):
        dir_paths = list(filter(lambda x: x.is_dir() and x, self._result_dir_path.iterdir()))
        if len(dir_paths) != 1:
            return True

        fauxpy_result_dir_path = dir_paths[0]
        if not self._has_score_files(fauxpy_result_dir_path):
            return True

        if not self._has_delta_time(fauxpy_result_dir_path):
            return True

    def _has_score_files(self, dir_path):
        dir_path_items = [str(x.name) for x in dir_path.iterdir()]

        if self._family == "sbfl":
            return ("Scores_Tarantula.csv" in dir_path_items and
                    "Scores_Ochiai.csv" in dir_path_items and
                    "Scores_Dstar.csv" in dir_path_items)
        elif self._family == "mbfl":
            return ("Scores_Metallaxis.csv" in dir_path_items and
                    "Scores_Muse.csv" in dir_path_items)
        elif self._family == "ps":
            score_files = filter(lambda x: x.startswith("Scores_") or x.endswith(".csv"), dir_path_items)
            return (NO_SWAPPED_INSTANCES_SCORES_FILE_NAME in dir_path_items or
                    NO_CANDIDATE_PREDICATES_SCORES_FILE_NAME in dir_path_items or
                    any(score_files))
        elif self._family == "st":
            return "Scores_default.csv" in dir_path_items
        else:
            raise Exception("This must not happen!")

    @staticmethod
    def _has_delta_time(dir_path):
        dir_path_items = [str(x.name) for x in dir_path.iterdir()]
        return "deltaTime.txt" in dir_path_items

    @classmethod
    def _is_csv_fishy(cls, csv_file):
        all_technique_scores = []
        all_statements = []
        with open(csv_file, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader, None)  # ignore the header
            for row in csv_reader:
                all_statements.append(row[0])
                all_technique_scores.append(float(row[1]))
        any_none_zero_item_values = any([x > 0 for x in all_technique_scores])
        is_values_all_same = cls.is_values_all_same(all_technique_scores)
        is_test_localized = cls.is_test_localized(all_statements)
        return not any_none_zero_item_values or is_values_all_same or is_test_localized

    @classmethod
    def is_values_all_same(cls, all_technique_scores: List[float]) -> bool:
        if len(all_technique_scores) <= 1:
            return False

        first_item = all_technique_scores[0]
        for item in all_technique_scores:
            if item != first_item:
                return False

        return True

    @classmethod
    def is_test_localized(cls, all_statements: List[str]) -> bool:
        for item in all_statements:
            if "test" in item:
                return True
        return False


class TimeoutItem(Item):
    def __init__(self, timeout_log_file_path: Path):
        self._timeout_log_file_path = timeout_log_file_path

        script_name_part = self._timeout_log_file_path.name.split(".")[0]
        self._load_info_from_script_name_part(script_name_part)

    def get_path(self):
        return self._timeout_log_file_path


class ResultManager:
    def __init__(self, result_items: List[ResultItem],
                 timeout_items: List[TimeoutItem],
                 script_items: List[ScriptItem],
                 garbage_manager: GarbageManager):
        self._result_items = result_items
        self._timeout_items = timeout_items
        self._script_items = script_items
        self._garbage_manager = garbage_manager

    def remove_bug_from_results_and_timeout(self,
                                            benchmark_name: str,
                                            bug_number: int):
        new_result_items = []
        for item in self._result_items:
            if (item.get_project_name() == benchmark_name and
                    item.get_bug_number() == bug_number):
                self._garbage_manager.move_to_garbage(item.get_path())
            else:
                new_result_items.append(item)
        self._result_items = new_result_items

        new_timeout_items = []
        for item in self._timeout_items:
            if (item.get_project_name() == benchmark_name and
                    item.get_bug_number() == bug_number):
                self._garbage_manager.move_to_garbage(item.get_path())
            else:
                new_timeout_items.append(item)
        self._timeout_items = new_timeout_items

    def remove_result_item(self, item: ResultItem):
        self._garbage_manager.move_to_garbage(item.get_path())
        self._result_items.remove(item)

    def remove_timeout_item(self, item: TimeoutItem):
        self._garbage_manager.move_to_garbage(item.get_path())
        self._timeout_items.remove(item)

    # def remove_result_item_by_id(self, experiment_id):
    #     items_found = list(
    #         filter(lambda x: x.get_experiment_id() == experiment_id, self._result_items))
    #     assert len(items_found) <= 1
    #     item = items_found[0]
    #     self._garbage_manager.move_to_garbage(item.get_path())
    #
    #     if item in self._result_items:
    #         self._result_items.remove(item)

    def get_multiple_result_items(self) -> List[ResultItem]:
        multiple_result_items = []
        for index1 in range(len(self._result_items)):
            for index2 in range(index1 + 1, len(self._result_items)):
                if self._result_items[index1] == self._result_items[index2]:
                    multiple_result_items.append(self._result_items[index1])
                    multiple_result_items.append(self._result_items[index2])

        return multiple_result_items

    def get_multiple_timeout_items(self):
        multiple_timeout_items = []
        for index1 in range(len(self._timeout_items)):
            for index2 in range(index1 + 1, len(self._timeout_items)):
                if self._timeout_items[index1] == self._timeout_items[index2]:
                    multiple_timeout_items.append(self._timeout_items[index1])
                    multiple_timeout_items.append(self._timeout_items[index2])

        return multiple_timeout_items

    def get_fishy_result_items(self) -> List[ResultItem]:
        fishy_result_items = []
        for result_item in self._result_items:
            if result_item.is_fishy():
                fishy_result_items.append(result_item)

        return fishy_result_items

    def get_corrupted_result_items(self) -> List[ResultItem]:
        corrupted_result_items = []
        for result_item in self._result_items:
            if result_item.is_corrupted():
                corrupted_result_items.append(result_item)

        return corrupted_result_items

    def get_normal_result_items(self):
        normal_result_items = []
        for result_item in self._result_items:
            if (not result_item.is_corrupted() and
                    not result_item.is_fishy()):
                normal_result_items.append(result_item)

        return normal_result_items

    def get_missing_statement_result_items(self):
        return self._get_missing_result_items("statement")

    def get_missing_function_result_items(self):
        return self._get_missing_result_items("function")

    def _get_missing_result_items(self, granularity: str) -> List[ScriptItem]:
        corrupted_list = self.get_corrupted_result_items()
        fishy_list = self.get_fishy_result_items()
        normal_list = self.get_normal_result_items()

        missing_statement_items = []
        for script_item in self._script_items:
            if (script_item.get_granularity() == granularity and
                    script_item not in corrupted_list + fishy_list + normal_list + self._timeout_items):
                missing_statement_items.append(script_item)

        return missing_statement_items

    def get_fixable_timeout_result_items(self) -> List[TimeoutItem]:
        fixable_timeout_items = []
        for timeout_item in self._timeout_items:
            if timeout_item.get_timeout() < 48:
                fixable_timeout_items.append(timeout_item)

        return fixable_timeout_items

    def get_unfixable_timeout_result_items(self) -> List[TimeoutItem]:
        unfixable_timeout_items = []
        for timeout_item in self._timeout_items:
            if timeout_item.get_timeout() == 48:
                unfixable_timeout_items.append(timeout_item)

        return unfixable_timeout_items

    def get_floating_timeout_items(self):
        garbage_timeout_items = []
        for timeout_item in self._timeout_items:
            if timeout_item not in self._script_items:
                garbage_timeout_items.append(timeout_item)

        return garbage_timeout_items

    def get_floating_result_items(self):
        garbage_result_items = []
        for result_item in self._result_items:
            if result_item not in self._script_items:
                garbage_result_items.append(result_item)

        return garbage_result_items


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict


def read_file_content(path) -> str:
    with path.open() as file:
        content = file.read()
    return content.strip()


def save_string_to_file(content: str,
                        file_path: Path):
    with file_path.open("w") as file:
        file.write(content)


def save_object_to_json(obj: Any,
                        file_path: Path):
    string_object = json.dumps(obj, indent=5)
    save_string_to_file(string_object, file_path)


def _load_script_items(scripts_path: Path) -> List[ScriptItem]:
    script_items = []
    for script_path in scripts_path.iterdir():
        script_object = ScriptItem(str(script_path.name))
        script_items.append(script_object)
    script_items.sort(key=lambda x: x.get_experiment_id())
    return script_items


def _load_result_timeout_items(results_path: Path,
                               correct_fishy_ids: List[int]) -> Tuple[List[ResultItem], List[TimeoutItem]]:
    result_items = []
    timeout_items = []

    for result_path in results_path.iterdir():
        if result_path.name not in ["Timeouts", GarbageManager.GarbageDirName]:
            result_object = ResultItem(result_path)
            if result_object.get_experiment_id() in correct_fishy_ids:
                result_object.set_is_correct_fishy(True)
            result_items.append(result_object)
    result_items.sort(key=lambda x: x.get_experiment_id())

    timeouts_path = results_path / "Timeouts"
    for timeout_path in timeouts_path.iterdir():
        timeout_object = TimeoutItem(timeout_path)
        timeout_items.append(timeout_object)
    timeout_items.sort(key=lambda x: x.get_experiment_id())

    return result_items, timeout_items


def _get_correct_fishy_ids():
    correct_fishy_ids = []
    correct_fishy_file_path = Path(CORRECT_FISHY_CSV_FILE_NAME)
    with correct_fishy_file_path.open("r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) == 1:
                correct_fishy_ids.append(int(row[0]))

    return correct_fishy_ids


def get_result_manager():
    path_manager = PathManager(PATH_ITEMS_FILE_NAME)
    results_path = path_manager.get_results_path()
    scripts_path = path_manager.get_scripts_path()

    correct_fishy_ids = _get_correct_fishy_ids()
    result_items, timeout_items = _load_result_timeout_items(results_path, correct_fishy_ids)
    script_items = _load_script_items(scripts_path)
    garbage_manager = GarbageManager(results_path)
    result_manager = ResultManager(result_items,
                                   timeout_items,
                                   script_items,
                                   garbage_manager)

    return result_manager
