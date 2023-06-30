import csv
import json
import pickle
import shutil
from pathlib import Path
from typing import List, Any, Dict

from csv_score_load_manager import CsvScoreItem
from entity_type import ScoredStatement, ScoredFunction, ScoredModule


class PathManager:
    _Path_item_file_name = "path_item.json"
    _Ground_truth_file_name = "ground_truth_info.json"
    _Size_counts_file_name = "size_counts.json"
    _Predicate_bug_info_file_name = "predicate_bug_info.json"
    _Predicate_selected_bug_info_file_name = "predicate_selected_bug_info.json"
    _Crashing_selected_bug_info_file_name = "crashing_selected_bug_info.json"
    _Statement_csv_score_directory_name = "csv_fauxpy_statement"
    _Function_csv_score_directory_name = "csv_fauxpy_function"
    _Module_csv_score_directory_name = "csv_fauxpy_module"
    _Latex_table_directory_name = "latex_table_info"
    _Java_paper_info_dir_path = "java_paper_input_for_latex"
    _Combine_fl_results_dir_name = "inputs_from_combine_fl"
    _Combine_fl_inputs_dir_name = "inputs_to_combine_fl"

    def __init__(self):
        self._results_path, self._workspace_path = self._load_path_items()

    def _load_path_items(self):
        path_item_object = load_json_to_object(self._Path_item_file_name)
        results_path = Path(path_item_object["RESULTS_PATH"])
        workspace_path = Path(path_item_object["WORKSPACE_PATH"])
        return results_path, workspace_path

    def get_results_path(self) -> Path:
        return self._results_path

    def get_workspace_path(self) -> Path:
        return self._workspace_path

    def get_ground_truth_file_name(self) -> str:
        return self._Ground_truth_file_name

    def get_size_counts_file_name(self) -> str:
        return self._Size_counts_file_name

    def get_predicate_bug_info_file_name(self) -> str:
        return self._Predicate_bug_info_file_name

    def get_predicate_selected_bug_info_file_name(self) -> str:
        return self._Predicate_selected_bug_info_file_name

    def get_crashing_selected_bug_info_file_name(self) -> str:
        return self._Crashing_selected_bug_info_file_name

    def get_function_csv_score_directory_path(self) -> Path:
        return self._get_csv_score_directory_path(self._Function_csv_score_directory_name)

    def get_module_csv_score_directory_path(self) -> Path:
        return self._get_csv_score_directory_path(self._Module_csv_score_directory_name)

    def get_statement_csv_score_directory_path(self):
        return self._get_csv_score_directory_path(self._Statement_csv_score_directory_name)

    def get_latex_table_dir_name(self) -> str:
        return self._Latex_table_directory_name

    def get_java_paper_info_dir_path(self) -> str:
        return self._Java_paper_info_dir_path

    def get_combine_fl_results_dir_name(self) -> str:
        return self._Combine_fl_results_dir_name

    def get_combine_fl_inputs_dir_name(self):
        return self._Combine_fl_inputs_dir_name

    @staticmethod
    def _get_csv_score_directory_path(csv_score_directory_name: str) -> Path:
        report_dir_path = Path(csv_score_directory_name)
        if report_dir_path.exists():
            shutil.rmtree(str(report_dir_path.absolute().resolve()))
        report_dir_path.mkdir()

        return report_dir_path


def load_json_to_object(file_name: str):
    with open(file_name) as file:
        data_dict = json.load(file)

    return data_dict


def save_object_to_json(obj: Any,
                        file_path: Path):
    string_object = json.dumps(obj, indent=5)
    save_string_to_file(string_object, file_path)


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
    def save(cls, obj: Any, file_name: str):
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


def save_string_to_file(content: str,
                        file_path: Path):
    with file_path.open("w") as file:
        file.write(content)


def save_csv_to_output_dir(table_list: List[List],
                           dir_name: str,
                           file_name: str):
    output_directory_path = Path(dir_name)
    file_path = output_directory_path / file_name
    with file_path.open("w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(table_list)


def clean_make_output_dir(dir_name: str):
    output_directory_path = Path(dir_name)
    if output_directory_path.exists():
        shutil.rmtree(str(output_directory_path.absolute().resolve()))

    if not output_directory_path.exists():
        output_directory_path.mkdir()

    return output_directory_path


def make_if_not_dir(dir_name: str):
    dir_path = Path(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()

    return dir_path


def save_score_items_to_given_directory_path(directory_path: Path,
                                             csv_score_items: List[CsvScoreItem]):
    report_dir_path = directory_path

    csv_header_items = ["Entity", "Score"]
    for csv_item in csv_score_items:
        current_file_name = f"{csv_item.get_project_name()}_" \
                            f"{csv_item.get_bug_number()}_" \
                            f"{csv_item.get_technique().name}_" \
                            f"{csv_item.get_granularity().name}.csv"
        current_file_path = report_dir_path / current_file_name

        with current_file_path.open("w") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(csv_header_items)
            for item in csv_item.get_scored_entities():
                if isinstance(item, ScoredStatement):
                    entity_str = f"{item.get_file_path()}::{item.get_line_number()}"
                elif isinstance(item, ScoredFunction):
                    function_range = item.get_function_range()
                    entity_str = f"{item.get_file_path()}::{item.get_function_name()}::{function_range[0]}::{function_range[1]}"
                elif isinstance(item, ScoredModule):
                    entity_str = item.get_file_path()
                else:
                    raise Exception()

                score = item.get_score()
                csv_writer.writerow([entity_str, score])
