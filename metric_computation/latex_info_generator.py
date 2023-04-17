# /flpy/granularity/family/technique/bugtype/metric

from pathlib import Path
from typing import Dict, List, Union, Tuple

from csv_score_load_manager import FLTechnique
from file_manager import load_json_to_object, save_string_to_file


class Constants:
    Root = "flpy"
    Statement = "stmt"
    Function = "func"
    Module = "mod"
    FAVG = "favg"
    SBFL = "sbfl"
    MBFL = "mbfl"
    PS = "ps"
    ST = "st"
    Tarantula = "tarantula"
    Ochiai = "ochiai"
    Dstar = "dstar"
    Metallaxis = "metallaxis"
    Muse = "muse"
    All = "all"
    Predicate = "pred"
    Crashing = "crash"
    Mutable = "mut"
    Dev = "dev"
    DS = "ds"
    Web = "web"
    Cli = "cli"
    Einspect = "einspect"
    At1 = "@1"
    At3 = "@3"
    At5 = "@5"
    At10 = "@10"
    Exam = "exam"
    Time = "time"
    Distance = "distance"


class LatexInfo:
    def __init__(self, latex_info_dir_path: Path):
        self._latex_info_dir_path = latex_info_dir_path

    def generate_data_latex_file(self):
        all_key_val_dict = {}
        all_tables_dict = self._load_all_tables()
        for key, value in all_tables_dict.items():
            key_val_dict = self._get_file_key_val_dict(key, value)
            all_key_val_dict = all_key_val_dict | key_val_dict

        all_key_val_str = self._get_all_key_val_as_str(all_key_val_dict)
        save_string_to_file(all_key_val_str, self._latex_info_dir_path / "data.tex")

    def _load_all_tables(self) -> Dict[str, List[List]]:
        json_file_path_list = list(self._latex_info_dir_path.rglob("*.json"))
        tables_dict = {}
        for item in json_file_path_list:
            file_name = item.name.split(".")[0]
            tables_dict[file_name] = load_json_to_object(str(item.absolute().resolve()))
        return tables_dict

    def _get_file_key_val_dict(self, file_name: str, table: List[List]) -> Dict[str, Union[float, int]]:
        file_key_val_dict = {}
        granularity_name = self._get_granularity_name(file_name)
        bug_type_name = self._get_bug_type_name(file_name)

        table_header = table[0]
        for index in range(1, len(table)):
            current_row = table[index]
            (family,
             technique,
             metric_dict) = self._get_info_dict_in_row(table_header, current_row)
            for metric_name, metric_value in metric_dict.items():
                current_latex_key = self._get_latex_key_for_metric(granularity_name,
                                                                   family,
                                                                   technique,
                                                                   bug_type_name,
                                                                   metric_name)
                file_key_val_dict[current_latex_key] = metric_value

        return file_key_val_dict

    @staticmethod
    def _get_granularity_name(file_name: str) -> str:
        name_parts = file_name.split("_")
        assert len(name_parts) == 4
        granularity_part = name_parts[1]

        if granularity_part == "statement":
            return Constants.Statement
        elif granularity_part == "function":
            return Constants.Function
        elif granularity_part == "module":
            return Constants.Module
        else:
            raise Exception()

    @staticmethod
    def _get_bug_type_name(file_name: str) -> str:
        name_parts = file_name.split("_")
        assert len(name_parts) == 4
        bug_part = name_parts[2]

        if bug_part == "all":
            return Constants.All
        elif bug_part == "predicate":
            return Constants.Predicate
        elif bug_part == "crashing":
            return Constants.Crashing
        elif bug_part == "mutable":
            return Constants.Mutable
        elif bug_part == "dev":
            return Constants.Dev
        elif bug_part == "ds":
            return Constants.DS
        elif bug_part == "web":
            return Constants.Web
        elif bug_part == "cli":
            return Constants.Cli
        else:
            raise Exception()

    def _get_info_dict_in_row(self,
                              table_header: List[str],
                              row: List[Union[str, int, float]]) -> Tuple[str, str, Dict[str, Union[int, float]]]:
        metric_dict = {}
        family, technique = self._get_family_metric(row[0])
        for index in range(1, len(row)):
            col_name = table_header[index]
            value = row[index]
            if col_name == "experiment_time_seconds":
                metric_dict[Constants.Time] = round(value)
            elif col_name == "@1%":
                metric_dict[Constants.At1] = round(value)
            elif col_name == "@3%":
                metric_dict[Constants.At3] = round(value)
            elif col_name == "@5%":
                metric_dict[Constants.At5] = round(value)
            elif col_name == "@10%":
                metric_dict[Constants.At10] = round(value)
            elif col_name == "exam_score":
                metric_dict[Constants.Exam] = round(value, 4)
            elif col_name == "cumulative_distance":
                if value is not None:
                    metric_dict[Constants.Distance] = round(value)

        return family, technique, metric_dict

    @staticmethod
    def _get_family_metric(string_name: str) -> Tuple[str, str]:
        if string_name == FLTechnique.Tarantula.name:
            return Constants.SBFL, Constants.Tarantula
        elif string_name == FLTechnique.Ochiai.name:
            return Constants.SBFL, Constants.Ochiai
        elif string_name == FLTechnique.DStar.name:
            return Constants.SBFL, Constants.Dstar
        elif string_name == FLTechnique.Metallaxis.name:
            return Constants.MBFL, Constants.Metallaxis
        elif string_name == FLTechnique.Muse.name:
            return Constants.MBFL, Constants.Muse
        elif string_name == FLTechnique.PS.name:
            return Constants.PS, Constants.FAVG
        elif string_name == FLTechnique.ST.name:
            return Constants.ST, Constants.FAVG
        elif string_name == "SBFL":
            return Constants.SBFL, Constants.FAVG
        elif string_name == "MBFL":
            return Constants.MBFL, Constants.FAVG
        else:
            raise Exception()

    @staticmethod
    def _get_latex_key_for_metric(granularity_name: str,
                                  family: str,
                                  technique: str,
                                  bug_type_name: str,
                                  metric_name: str) -> str:
        current_latex_key = (f"/{Constants.Root}/"
                             f"{granularity_name}/"
                             f"{family}/"
                             f"{technique}/"
                             f"{bug_type_name}/"
                             f"{metric_name}")

        return current_latex_key

    @staticmethod
    def _get_all_key_val_as_str(all_key_val_dict):
        str_item_list = []
        for key, value in all_key_val_dict.items():
            current_latex_item = f"\pgfkeyssetvalue{{{key}}}{{{value}}}"
            str_item_list.append(current_latex_item)

        return "\n".join(str_item_list)
