from pathlib import Path
from typing import Dict, List

from file_manager import save_string_to_file, load_json_to_object


class Constants:
    Root = "flpy"
    At = "@X"
    Time = "time"
    All = "all"


class LatexInfo:
    Data_file_name = "data.text"
    Number_of_projects = 135

    def __init__(self,
                 info_dir_path: Path,
                 project_count_file_path: Path):
        self._info_dir_path = info_dir_path
        self._project_count = load_json_to_object(str(project_count_file_path.absolute().resolve()))
        self._total_row_dict = {}

    @staticmethod
    def _get_all_key_val_as_str(all_key_val_dict):
        str_item_list = []
        for key, value in all_key_val_dict.items():
            current_latex_item = f"\pgfkeyssetvalue{{{key}}}{{{value}}}"
            str_item_list.append(current_latex_item)

        return "\n".join(str_item_list)

    def generate(self):
        all_key_val_dict = self._get_all_key_value_dict()
        total_key_val_dict = self._get_total_key_val_dict()
        all_key_val_dict = all_key_val_dict | total_key_val_dict
        all_key_val_str = self._get_all_key_val_as_str(all_key_val_dict)
        save_string_to_file(all_key_val_str, self._info_dir_path / self.Data_file_name)

    def _get_all_key_value_dict(self) -> Dict:
        all_key_val_dict = {}
        all_tables_dict = self._load_all_tables()
        for project, values in all_tables_dict.items():
            project_key_value_dict = self._get_project_key_value_dict(project, values)
            all_key_val_dict = all_key_val_dict | project_key_value_dict

        return all_key_val_dict

    def _load_all_tables(self) -> Dict[str, List[List]]:
        json_file_path_list = list(self._info_dir_path.rglob("fauxpy*.json"))
        tables_dict = {}
        for item in json_file_path_list:
            project_name = item.name.split("_")[2]
            if project_name == "youtube":
                project_name = project_name + "_dl"
            tables_dict[project_name] = load_json_to_object(str(item.absolute().resolve()))
        return tables_dict

    def _get_project_key_value_dict(self,
                                    project_name: str,
                                    values: List[List]) -> Dict:
        project_key_value_dict = {}

        techniques = ["Tarantula", "Ochiai", "DStar",
                      "Metallaxis", "Muse", "PS",
                      "ST"]
        families = ["SBFL", "MBFL", "PS",
                    "ST"]

        header_row = values[0]
        assert header_row[0] == "technique"
        assert header_row[1] == "experiment_time_seconds"
        assert header_row[7] == "@5"

        body_rows = values[1:]

        for row in body_rows:
            technique_name = row[0]
            if technique_name in techniques:
                at_x_value = row[7]
                at_x_key = self._get_key_for_project_technique_metric(project_name,
                                                                      technique_name,
                                                                      Constants.At)

                total_key = f"{technique_name}:{Constants.At}"
                if total_key not in self._total_row_dict.keys():
                    self._total_row_dict[total_key] = 0
                self._total_row_dict[total_key] += int(at_x_value)

                project_key_value_dict[at_x_key] = int(at_x_value)

            if technique_name in families:
                average_time_value = row[1]
                average_time_key = self._get_key_for_project_technique_metric(project_name,
                                                                              technique_name,
                                                                              Constants.Time)

                total_key = f"{technique_name}:{Constants.Time}"
                if total_key not in self._total_row_dict.keys():
                    self._total_row_dict[total_key] = 0
                self._total_row_dict[total_key] += (float(average_time_value) *
                                                    self._project_count[project_name])

                project_key_value_dict[average_time_key] = float(average_time_value)

        return project_key_value_dict

    @staticmethod
    def _get_key_for_project_technique_metric(project_name: str,
                                              technique_name: str,
                                              metric_name: str) -> str:
        # /flpy/project name/technique name/metric
        return f"/flpy/{project_name}/{technique_name}/{metric_name}"

    def _get_total_key_val_dict(self):
        total_key_val_dict = {}

        for key, value in self._total_row_dict.items():
            technique_name = key.split(":")[0]
            metric_name = key.split(":")[1]
            metric_key = self._get_key_for_project_technique_metric(Constants.All,
                                                                    technique_name,
                                                                    metric_name)
            if metric_name == Constants.Time:
                total_key_val_dict[metric_key] = value / self.Number_of_projects
            else:
                total_key_val_dict[metric_key] = value

        return total_key_val_dict
