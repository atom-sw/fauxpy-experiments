from enum import Enum
from pathlib import Path
from typing import Dict, List

import common


class FLTechnique(Enum):
    Tarantula = 0
    Ochiai = 1
    DStar = 2
    Metallaxis = 3
    Muse = 4
    PS = 5
    ST = 6


class FLGranularity(Enum):
    Statement = 0
    Function = 1


class CsvScoreItem:
    def __init__(self,
                 csv_paths: List[Path],
                 script_id: int,
                 project_name: str,
                 bug_number: int,
                 localization_technique: FLTechnique,
                 granularity: FLGranularity):
        self.csv_paths = csv_paths
        self.script_id = script_id
        self.project_name = project_name
        self.bug_number = bug_number
        self.localization_technique = localization_technique
        self.granularity = granularity

    def _pretty_representation(self):
        csv_files = [x.name for x in self.csv_paths]
        return (f"{self.script_id} "
                f"{self.project_name} "
                f"{self.bug_number} "
                f"{self.localization_technique.name} "
                f"{self.granularity.name} "
                f"{csv_files}")

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()


class ResultManager:
    def __init__(self, csv_score_items: List[CsvScoreItem],
                 ground_truth_info: Dict):
        self._csv_score_items = csv_score_items
        self._ground_truth_info = ground_truth_info

    def get_all_csv_score_items(self):
        return self._csv_score_items


class CsvScoreItemLoadManager:
    def __init__(self, results_path: Path):
        self._results_path = results_path

    @classmethod
    def _get_family_csv_score_items(cls, result_path: Path) -> List[CsvScoreItem]:
        family_csv_score_items = []
        name_parts = result_path.name.split("_")
        script_id = int(name_parts[0])
        project_name = name_parts[3]
        bug_num = int(name_parts[4])
        family = name_parts[5]
        if name_parts[6] == "statement":
            granularity = FLGranularity.Statement
        elif name_parts[6] == "function":
            granularity = FLGranularity.Function
        else:
            raise Exception("This should never happen.")

        result_path_dirs = list(filter(lambda x: x.is_dir(), result_path.iterdir()))
        assert len(result_path_dirs) == 1
        fauxpy_result_path = result_path_dirs[0]
        fauxpy_csv_paths = list(filter(lambda x: x.name.endswith(".csv"), fauxpy_result_path.iterdir()))

        cls._check_fauxpy_csv_paths(family, fauxpy_csv_paths)

        if family == "ps":
            current_csv_score = CsvScoreItem(fauxpy_csv_paths,
                                             script_id,
                                             project_name,
                                             bug_num,
                                             FLTechnique.PS,
                                             granularity)
            family_csv_score_items.append(current_csv_score)
        else:
            for csv_score_path in fauxpy_csv_paths:
                technique = cls._get_technique_from_csv_name(csv_score_path.name)
                current_csv_score = CsvScoreItem([csv_score_path],
                                                 script_id,
                                                 project_name,
                                                 bug_num,
                                                 technique,
                                                 granularity)
                family_csv_score_items.append(current_csv_score)

        return family_csv_score_items

    def load_csv_score_items(self) -> List[CsvScoreItem]:
        csv_score_items = []
        for item in self._results_path.iterdir():
            if item.name not in ["Timeouts", "Garbage"]:
                family_csv_score_items = self._get_family_csv_score_items(item)
                csv_score_items += family_csv_score_items
        return csv_score_items

    @classmethod
    def _check_fauxpy_csv_paths(cls, family, fauxpy_csv_paths):
        fauxpy_csv_file_names = [x.name for x in fauxpy_csv_paths]
        if family == "sbfl":
            assert len(fauxpy_csv_paths) == 3
            assert "Scores_Tarantula.csv" in fauxpy_csv_file_names
            assert "Scores_Ochiai.csv" in fauxpy_csv_file_names
            assert "Scores_Dstar.csv" in fauxpy_csv_file_names
        elif family == "mbfl":
            assert len(fauxpy_csv_paths) == 2
            assert "Scores_Metallaxis.csv" in fauxpy_csv_file_names
            assert "Scores_Muse.csv" in fauxpy_csv_file_names
        elif family == "ps":
            assert len(fauxpy_csv_paths) >= 1
            assert any([x.startswith("Scores_") and x.endswith(".csv") for x in fauxpy_csv_file_names])
        elif family == "st":
            assert len(fauxpy_csv_paths) == 1
            assert "Scores_default.csv" in fauxpy_csv_file_names
        else:
            raise Exception("This should never be reached.")

    @classmethod
    def _get_technique_from_csv_name(cls, csv_file_name) -> FLTechnique:
        if "Scores_Tarantula.csv" in csv_file_name:
            return FLTechnique.Tarantula
        if "Scores_Ochiai.csv" in csv_file_name:
            return FLTechnique.Ochiai
        if "Scores_Dstar.csv" in csv_file_name:
            return FLTechnique.DStar
        if "Scores_Metallaxis.csv" in csv_file_name:
            return FLTechnique.Metallaxis
        if "Scores_Muse.csv" in csv_file_name:
            return FLTechnique.Muse
        if "Scores_default.csv" in csv_file_name:
            return FLTechnique.ST


def get_result_manager():
    path_manager = common.PathManager()
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    csv_score_items = csv_score_item_load_manager.load_csv_score_items()
    ground_truth_info = common.load_json_to_dictionary(path_manager.get_ground_truth_path())
    result_manager = ResultManager(csv_score_items, ground_truth_info)

    return result_manager
