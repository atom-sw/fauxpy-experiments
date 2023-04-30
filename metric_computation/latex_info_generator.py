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
    Java_exam = "javaexam"
    Time = "time"
    Distance = "distance"
    Combine_fl = "comb"
    Average_fl = "avfl"
    All_families = "alfa"
    Sbfl_st = "sbst"
    Python = "python"
    Java = "java"


class LatexInfo:
    Data_file_name = "data.tex"
    Java_file_name = "java_statement_all_overall.json"

    def __init__(self,
                 latex_info_dir_path: Path,
                 java_paper_info_dir_path: Path,
                 combine_fl_results_dir_path: Path):
        self._latex_info_dir_path = latex_info_dir_path
        self._java_paper_info_dir_path = java_paper_info_dir_path
        self._combine_fl_results_dir_path = combine_fl_results_dir_path

    def generate_data_latex_file(self):
        python_key_val_dict = {}
        all_tables_dict = self._load_all_tables()
        for key, value in all_tables_dict.items():
            key_val_dict = self._get_file_key_val_dict(key, value)
            python_key_val_dict = python_key_val_dict | key_val_dict

        java_info_file_path = self._java_paper_info_dir_path / self.Java_file_name
        java_key_val_dict = load_json_to_object(str(java_info_file_path.absolute().resolve()))
        all_key_val_dict = python_key_val_dict | java_key_val_dict

        combine_fl_key_val_dict = self._get_combine_fl_key_val_dict(all_key_val_dict)
        all_key_val_dict = all_key_val_dict | combine_fl_key_val_dict

        all_key_val_str = self._get_all_key_val_as_str(all_key_val_dict)
        save_string_to_file(all_key_val_str, self._latex_info_dir_path / self.Data_file_name)

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
            elif col_name == "e_inspect":
                metric_dict[Constants.Einspect] = round(value)
            elif col_name == "@1%":
                metric_dict[Constants.At1] = round(value)
            elif col_name == "@3%":
                metric_dict[Constants.At3] = round(value)
            elif col_name == "@5%":
                metric_dict[Constants.At5] = round(value)
            elif col_name == "@10%":
                metric_dict[Constants.At10] = round(value)
            elif col_name == "exam_score":
                metric_dict[Constants.Exam] = value
            elif col_name == "java_exam_score":
                metric_dict[Constants.Java_exam] = value
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
                                  metric_name: str,
                                  language_name: str = Constants.Python) -> str:
        current_latex_key = (f"/{Constants.Root}/"
                             f"{granularity_name}/"
                             f"{family}/"
                             f"{technique}/"
                             f"{bug_type_name}/"
                             f"{metric_name}")

        if language_name == Constants.Java:
            current_latex_key = f"{current_latex_key}/{Constants.Java}"

        return current_latex_key

    @staticmethod
    def _get_all_key_val_as_str(all_key_val_dict):
        str_item_list = []
        for key, value in all_key_val_dict.items():
            current_latex_item = f"\pgfkeyssetvalue{{{key}}}{{{value}}}"
            str_item_list.append(current_latex_item)

        return "\n".join(str_item_list)

    def _get_combine_fl_key_val_dict(self, all_key_val_dict: Dict[str, float]) -> Dict[str, float]:
        file_path_list = list(self._combine_fl_results_dir_path.rglob("*.json"))

        combine_fl_key_val_avg_dict = {}

        combine_fl_key_val_dict = {}
        for file_path in file_path_list:
            file_path_parts = file_path.name.split(".")[0].split("_")
            language = file_path_parts[1]
            granularity = file_path_parts[2]
            technique = file_path_parts[3]

            json_dict = load_json_to_object(str(file_path.absolute().resolve()))

            if granularity == "statement":
                const_granularity_string = Constants.Statement
            elif granularity == "function":
                const_granularity_string = Constants.Function
            elif granularity == "module":
                const_granularity_string = Constants.Module
            else:
                raise Exception()

            if language == Constants.Python and const_granularity_string == Constants.Statement:
                time_cost = self._get_time_for_combine_fl_statement(all_key_val_dict, language,
                                                                    const_granularity_string, technique)
                latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                           Constants.Combine_fl,
                                                           technique,
                                                           Constants.All,
                                                           Constants.Time,
                                                           language)
                combine_fl_key_val_dict[latex_key] = time_cost

            latex_key = None
            for j_key, j_value in json_dict.items():
                if j_key == "@1%":
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.At1,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value
                elif j_key == "@3%":
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.At3,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value
                elif j_key == "@5%":
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.At5,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value
                elif j_key == "@10%":
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.At10,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value
                elif j_key == "python_e_inspect":
                    if language == Constants.Java:
                        continue
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.Einspect,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = round(j_value)
                elif j_key == "python_exam":
                    if language == Constants.Java:
                        continue
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.Exam,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value
                elif j_key == "java_exam":
                    latex_key = self._get_latex_key_for_metric(const_granularity_string,
                                                               Constants.Combine_fl,
                                                               technique,
                                                               Constants.All,
                                                               Constants.Java_exam,
                                                               language)
                    combine_fl_key_val_dict[latex_key] = j_value

                if latex_key is not None:
                    # Collect family average info
                    key_segments = latex_key.split("/")
                    latex_key = None
                    assert len(key_segments) == 7 or len(key_segments) == 8

                    avg_latex_key = f"/{'/'.join(key_segments[1:4])}/{Constants.FAVG}/{'/'.join(key_segments[5:])}"
                    if avg_latex_key not in combine_fl_key_val_avg_dict:
                        combine_fl_key_val_avg_dict[avg_latex_key] = 0
                    combine_fl_key_val_avg_dict[avg_latex_key] += j_value

        for key_avg, value_avg in combine_fl_key_val_avg_dict.items():
            # Compute average
            value = value_avg / 2
            if "@" in key_avg or "einspect" in key_avg:
                value = round(value)
            combine_fl_key_val_avg_dict[key_avg] = value

        combine_fl_key_val_dict = combine_fl_key_val_dict | combine_fl_key_val_avg_dict

        return combine_fl_key_val_dict

    def _get_time_for_combine_fl_statement(self,
                                           all_key_val_dict: Dict[str, float],
                                           language: str,
                                           granularity: str,
                                           combine_fl_technique: str) -> float:
        assert language == Constants.Python
        assert granularity == Constants.Statement
        assert combine_fl_technique == Constants.All_families or combine_fl_technique == Constants.Sbfl_st

        latex_key = self._get_latex_key_for_metric(granularity,
                                                   Constants.SBFL,
                                                   Constants.Ochiai,
                                                   Constants.All,
                                                   Constants.Time,
                                                   language)
        time_sbfl = all_key_val_dict[latex_key]

        latex_key = self._get_latex_key_for_metric(granularity,
                                                   Constants.MBFL,
                                                   Constants.Metallaxis,
                                                   Constants.All,
                                                   Constants.Time,
                                                   language)
        time_mbfl = all_key_val_dict[latex_key]

        latex_key = self._get_latex_key_for_metric(granularity,
                                                   Constants.PS,
                                                   Constants.FAVG,
                                                   Constants.All,
                                                   Constants.Time,
                                                   language)
        time_ps = all_key_val_dict[latex_key]

        latex_key = self._get_latex_key_for_metric(granularity,
                                                   Constants.ST,
                                                   Constants.FAVG,
                                                   Constants.All,
                                                   Constants.Time,
                                                   language)
        time_st = all_key_val_dict[latex_key]

        if combine_fl_technique == Constants.All_families:
            time_cost = time_sbfl + time_mbfl + time_ps + time_st
        elif combine_fl_technique == Constants.Sbfl_st:
            time_cost = time_sbfl + time_st
        else:
            raise Exception()

        return time_cost

    def _get_combine_fl_key_val_dict_family_average(self, combine_fl_key_val_dict: Dict[str, float]):
        pass
