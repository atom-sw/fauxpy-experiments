import csv
import json
import os.path
from pathlib import Path
from typing import Any, List

NO_SWAPPED_INSTANCES_SCORES_FILE_NAME = "Scores_fauxpy_no_swapped_instances.csv"
NO_CANDIDATE_PREDICATES_SCORES_FILE_NAME = "Scores_fauxpy_no_candidate_predicates.csv"


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


class ScriptItem(Item):
    def __init__(self, script_name: str):
        self._script_name = script_name

        script_name_part = self._script_name.split(".")[0]
        self._load_info_from_script_name_part(script_name_part)


class ResultItem(Item):
    def __init__(self, result_dir_path: Path):
        self._result_dir_path = result_dir_path

        script_name_part = "_".join(str(result_dir_path.name).split("_")[:-1])
        self._load_info_from_script_name_part(script_name_part)
        self._creation_time = os.path.getctime(str(result_dir_path.absolute().resolve()))

    def is_fishy(self):
        if self.is_corrupted():
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

    @staticmethod
    def _is_csv_fishy(csv_file):
        all_technique_scores = []
        with open(csv_file, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader, None)  # ignore the header
            for row in csv_reader:
                all_technique_scores.append(float(row[1]))
        any_none_zero_item_values = any([x > 0 for x in all_technique_scores])
        return not any_none_zero_item_values


class TimeoutItem(Item):
    def __init__(self, timeout_log_file_path: Path):
        self._timeout_log_file_path = timeout_log_file_path

        script_name_part = self._timeout_log_file_path.name.split(".")[0]
        self._load_info_from_script_name_part(script_name_part)


class ResultManager:
    def __init__(self, result_items: List[ResultItem],
                 timeout_items: List[TimeoutItem],
                 script_items: List[ScriptItem]):
        self._result_items = result_items
        self._timeout_items = timeout_items
        self._script_items = script_items

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

    def get_garbage_timeout_items(self):
        garbage_timeout_items = []
        for timeout_item in self._timeout_items:
            if timeout_item not in self._script_items:
                garbage_timeout_items.append(timeout_item)

        return garbage_timeout_items

    def get_garbage_result_items(self):
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
