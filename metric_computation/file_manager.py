import csv
import json
import pickle
import shutil
from pathlib import Path
from typing import List, Any

from csv_score_load_manager import CsvScoreItem

OUTPUT_DIRECTORY_NAME = "output"
FUNCTION_CSV_SCORE_DIR_NAME = "function_csv"


class PathManager:
    _Path_item_file_name = "path_item.json"
    _Ground_truth_file_name = "ground_truth_info.json"
    _Line_counts_file_name = "line_counts.json"

    def __init__(self):
        self._results_path, self._workspace_path = self._load_path_items()

    def _load_path_items(self):
        path_item_object = load_json_to_dictionary(self._Path_item_file_name)
        results_path = Path(path_item_object["RESULTS_PATH"])
        workspace_path = Path(path_item_object["WORKSPACE_PATH"])
        return results_path, workspace_path

    def get_results_path(self) -> Path:
        return self._results_path

    def get_workspace_path(self) -> Path:
        return self._workspace_path

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


FIRST_CALL = False


def _get_output_directory_path() -> Path:
    global FIRST_CALL

    output_directory_path = Path(OUTPUT_DIRECTORY_NAME)
    if output_directory_path.exists() and not FIRST_CALL:
        shutil.rmtree(str(output_directory_path.absolute().resolve()))

    FIRST_CALL = True

    if not output_directory_path.exists():
        output_directory_path.mkdir()

    return output_directory_path


def save_as_csv_file(table_list: List[List],
                     file_name: str):
    output_directory_path = _get_output_directory_path()
    file_path = output_directory_path / file_name
    with file_path.open("w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(table_list)


def save_function_csv_score_items(function_csv_score_items: List[CsvScoreItem]):
    report_dir_path = Path(FUNCTION_CSV_SCORE_DIR_NAME)
    if report_dir_path.exists():
        shutil.rmtree(str(report_dir_path.absolute().resolve()))
    report_dir_path.mkdir()

    csv_header_items = ["Entity", "Score"]
    for function_csv_item in function_csv_score_items:
        current_file_name = f"{function_csv_item.get_project_name()}_" \
                            f"{function_csv_item.get_bug_number()}_" \
                            f"{function_csv_item.get_technique().name}_" \
                            f"{function_csv_item.get_granularity().name}.csv"
        current_file_path = report_dir_path / current_file_name

        with current_file_path.open("w") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(csv_header_items)
            for item in function_csv_item.get_scored_entities():
                function_range = item.get_function_range()
                entity_str = f"{item.get_file_path()}::{item.get_function_name()}::{function_range[0]}::{function_range[1]}"
                score = item.get_score()
                csv_writer.writerow([entity_str, score])
