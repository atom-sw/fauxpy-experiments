import json
from pathlib import Path


class PathManager:
    _Workspace_file_name = "workspace.json"
    _Ground_truth_file_name = "ground_truth_info.json"

    def __init__(self):
        self._results_path = self._load_path_items()

    def _load_path_items(self):
        workspace_object = load_json_to_dictionary(self._Workspace_file_name)
        results_path = Path(workspace_object["RESULTS_PATH"])
        return results_path

    def get_results_path(self) -> Path:
        return self._results_path

    def get_ground_truth_path(self) -> str:
        return self._Ground_truth_file_name


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict
