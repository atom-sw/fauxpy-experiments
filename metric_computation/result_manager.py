from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import file_manager
from metrics import ScoredEntity, ScoredStatement, ScoredFunction, EInspect


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
                 granularity: FLGranularity,
                 scored_entities: List[ScoredEntity]):
        self._csv_paths = csv_paths
        self._script_id = script_id
        self._project_name = project_name
        self._bug_number = bug_number
        self._localization_technique = localization_technique
        self._granularity = granularity
        self._scored_entities = scored_entities
        self._e_inspect = None

    def _pretty_representation(self):
        csv_files = [x.name for x in self._csv_paths]
        return (f"{self._script_id} "
                f"{self._project_name} "
                f"{self._bug_number} "
                f"{self._localization_technique.name} "
                f"{self._granularity.name} "
                f"{csv_files}")

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    def get_script_id(self) -> int:
        return self._script_id

    def get_technique(self):
        return self._localization_technique

    def get_scored_entities(self):
        return self._scored_entities

    def get_project_name(self) -> str:
        return self._project_name

    def get_bug_number(self) -> int:
        return self._bug_number

    def get_e_inspect(self) -> Optional[float]:
        return self._e_inspect


class ResultManager:
    def __init__(self, csv_score_items: List[CsvScoreItem],
                 ground_truth_info_dict: Dict,
                 line_counts_dict: Dict):
        self._csv_score_items = csv_score_items
        self._ground_truth_info_dict = ground_truth_info_dict
        self._line_counts_dict = line_counts_dict

    def compute_e_inspect_for_all(self):
        for item in self._csv_score_items:
            bug_key = f"{item.get_project_name()}:{item.get_bug_number()}"
            bug_ground_truth_dict = self._ground_truth_info_dict[bug_key]
            bug_line_count = self._line_counts_dict[bug_key]
            e_inspect_object = EInspect(item.get_scored_entities(), bug_line_count, bug_ground_truth_dict)
            e_inspect_value = e_inspect_object.get_e_inspect()
            item._e_inspect = e_inspect_value

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
            score_table = cls.load_csv_score_file(fauxpy_csv_paths, family, granularity)
            current_csv_score = CsvScoreItem(fauxpy_csv_paths,
                                             script_id,
                                             project_name,
                                             bug_num,
                                             FLTechnique.PS,
                                             granularity,
                                             score_table)
            family_csv_score_items.append(current_csv_score)
        else:
            for csv_score_path in fauxpy_csv_paths:
                score_table = cls.load_csv_score_file([csv_score_path], family, granularity)
                technique = cls._get_technique_from_csv_name(csv_score_path.name)
                current_csv_score = CsvScoreItem([csv_score_path],
                                                 script_id,
                                                 project_name,
                                                 bug_num,
                                                 technique,
                                                 granularity,
                                                 score_table)
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

    @classmethod
    def load_csv_score_file(cls,
                            csv_paths: List[Path],
                            family: str,
                            granularity: FLGranularity) -> List[ScoredEntity]:
        if granularity == FLGranularity.Statement:
            if family in ["sbfl", "mbfl"]:
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_sbfl_mbfl_statement_items(csv_file_content)
            elif family == "ps":
                # TODO: Fix this.
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_ps_statement_items(csv_file_content)
            else:
                raise Exception("This should never happen.")
        elif granularity == FLGranularity.Function:
            if family == "ps":
                # TODO: Fix this.
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_function_items(csv_file_content)
            else:
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_function_items(csv_file_content)
        else:
            raise Exception("This should never happen.")

        scored_entity_items.sort(key=lambda x: x.get_score(), reverse=True)
        return scored_entity_items

    @classmethod
    def csv_content_to_scored_sbfl_mbfl_statement_items(cls,
                                                        csv_file_content: List[List[str]]) -> List[ScoredStatement]:
        scored_statement_items = []
        for row in csv_file_content:
            col1_parts = row[0].split("::")
            file_path_parts = col1_parts[0].split("/")
            relative_file_path = "/".join(file_path_parts[6:])
            line_number = int(col1_parts[1])
            score = float(row[1])
            scored_statement_item = ScoredStatement(relative_file_path, score, line_number)
            scored_statement_items.append(scored_statement_item)

        return scored_statement_items

    @classmethod
    def csv_content_to_scored_ps_statement_items(cls,
                                                 csv_file_content: List[List[str]]) -> List[ScoredStatement]:
        scored_statement_items = []
        for row in csv_file_content:
            col1_parts = row[0].split("::")
            file_path_parts = col1_parts[0].split("/")
            relative_file_path = "/".join(file_path_parts[6:])
            line_start = int(col1_parts[1])
            line_end = int(col1_parts[2])
            score = float(row[1])
            for line_number in range(line_start, line_end + 1):
                scored_statement_item = ScoredStatement(relative_file_path, score, line_number)
                scored_statement_items.append(scored_statement_item)

        return scored_statement_items

    @classmethod
    def csv_content_to_scored_function_items(cls,
                                             csv_file_content: List[List[str]]):
        scored_function_items = []
        for row in csv_file_content:
            col1_parts = row[0].split("::")
            file_path_parts = col1_parts[0].split("/")
            relative_file_path = "/".join(file_path_parts[6:])
            function_name = col1_parts[1]
            line_start = int(col1_parts[2])
            line_end = int(col1_parts[3])
            function_range = (line_start, line_end)
            score = float(row[1])
            scored_function_item = ScoredFunction(relative_file_path, score, function_range, function_name)
            scored_function_items.append(scored_function_item)

        return scored_function_items


def get_result_manager():
    path_manager = file_manager.PathManager()
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    # csv_score_items = file_manager.Cache.load("csv_score_items")
    # if csv_score_items is None:
    #     csv_score_items = csv_score_item_load_manager.load_csv_score_items()
    #     file_manager.Cache.save(csv_score_items, "csv_score_items")
    csv_score_items = csv_score_item_load_manager.load_csv_score_items()
    ground_truth_info = file_manager.load_json_to_dictionary(path_manager.get_ground_truth_path())
    line_counts_info = file_manager.load_json_to_dictionary(path_manager.get_line_counts_path())
    result_manager = ResultManager(csv_score_items, ground_truth_info, line_counts_info)

    return result_manager
