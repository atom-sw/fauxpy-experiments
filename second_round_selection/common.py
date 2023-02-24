import json
from pathlib import Path
from typing import Any


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


class ScriptItem:
    def __init__(self, script_name: str):
        self.script_name = script_name

        (self._experiment_id,
         self._timeout,
         self._memory,
         self._project_name,
         self._bug_num,
         self._family,
         self._granularity) = self._load_info_from_name()

    def _load_info_from_name(self) -> tuple[int, int, int, str, int, str, str]:
        file_name = self.script_name.split(".")[0]
        name_parts = file_name.split("_")
        experiment_id = int(name_parts[0])
        timeout = int(name_parts[1][:-1])
        memory = int(name_parts[2][:-1])
        project_name = name_parts[3]
        bug_num = int(name_parts[4])
        family = name_parts[5]
        granularity = name_parts[6]
        return experiment_id, timeout, memory, project_name, bug_num, family, granularity

    def __str__(self):
        return (f"{self.script_name}, "
                f"{self._experiment_id}, "
                f"{self._timeout}, "
                f"{self._memory}, "
                f"{self._project_name}, "
                f"{self._bug_num}, "
                f"{self._family}, "
                f"{self._granularity}")

    def get_experiment_id(self) -> int:
        return self._experiment_id


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
