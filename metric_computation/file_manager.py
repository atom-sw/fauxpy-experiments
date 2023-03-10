import csv
import json
import pickle
from pathlib import Path
from typing import List, Any


class PathManager:
    _Path_item_file_name = "path_item.json"
    _Ground_truth_file_name = "ground_truth_info.json"
    _Line_counts_file_name = "line_counts.json"

    def __init__(self):
        self._results_path = self._load_path_items()

    def _load_path_items(self):
        path_item_object = load_json_to_dictionary(self._Path_item_file_name)
        results_path = Path(path_item_object["RESULTS_PATH"])
        return results_path

    def get_results_path(self) -> Path:
        return self._results_path

    def get_ground_truth_path(self) -> str:
        return self._Ground_truth_file_name

    def get_line_counts_path(self) -> str:
        return self._Line_counts_file_name


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict


def load_csv_content_file(csv_path: Path) -> List[List[str]]:
    rows = []
    with csv_path.open("r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            rows.append(row)
    return rows


class Cache:
    _Cache_directory_name = "cache"

    @classmethod
    def load(cls, file_name: str):
        cache_dir_path = cls._get_cache_dir_path()
        cached_file_path = cache_dir_path / file_name
        if cached_file_path.exists():
            with cached_file_path.open("rb") as file:
                loaded_object = pickle.load(file)
            return loaded_object
        return None

    @classmethod
    def save(cls, obj: Any, file_name):
        cache_dir_path = cls._get_cache_dir_path()
        cached_file_path = cache_dir_path / file_name
        with cached_file_path.open("wb") as file:
            pickle.dump(obj, file)

    @classmethod
    def _get_cache_dir_path(cls):
        cache_dir_path = Path(cls._Cache_directory_name)
        if not cache_dir_path.exists():
            cache_dir_path.mkdir()
        return cache_dir_path


def load_file_content(file_path: Path):
    with file_path.open("r") as file:
        content = file.read()

    return content


def save_as_csv_file(table_list: List[List],
                     file_name: str):
    with open(file_name, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(table_list)
