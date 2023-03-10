from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import file_manager
from literature_metrics import ScoredEntity, ScoredStatement, EInspect


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


class MetricVal:
    def __init__(self,
                 experiment_time: float,
                 e_inspect: float,
                 exam_score: float):
        self._experiment_time = experiment_time
        self._e_inspect = e_inspect
        self._exam_score = exam_score

    def get_experiment_time(self) -> float:
        return self._experiment_time

    def get_e_inspect(self) -> float:
        return self._e_inspect

    def get_exam_score(self) -> float:
        return self._exam_score


class CsvScoreItem:
    def __init__(self,
                 csv_paths: List[Path],
                 script_id: int,
                 project_name: str,
                 bug_number: int,
                 localization_technique: FLTechnique,
                 granularity: FLGranularity,
                 scored_entities: List[ScoredEntity],
                 experiment_time_seconds: float):
        self._csv_paths = csv_paths
        self._script_id = script_id
        self._project_name = project_name
        self._bug_number = bug_number
        self._localization_technique = localization_technique
        self._granularity = granularity
        self._scored_entities = scored_entities
        self._experiment_time_seconds = experiment_time_seconds
        self._metric_val = None

    def _pretty_representation(self):
        csv_files = [x.name for x in self._csv_paths]
        return (f"{self._script_id} "
                f"{self._project_name} "
                f"{self._bug_number} "
                f"{self._localization_technique.name} "
                f"{self._granularity.name} "
                f"SEC:{self._experiment_time_seconds} "
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

    def get_experiment_time_seconds(self) -> float:
        return self._experiment_time_seconds

    def set_metric_val(self, metric_val: MetricVal):
        self._metric_val = metric_val

    def get_metric_val(self) -> MetricVal:
        return self._metric_val

    def get_granularity(self) -> FLGranularity:
        return self._granularity


class ResultManager:
    def __init__(self, csv_score_items: List[CsvScoreItem],
                 ground_truth_info_dict: Dict,
                 line_counts_dict: Dict):
        self._csv_score_items = csv_score_items
        assert any([x.get_granularity() == FLGranularity.Statement for x in self._csv_score_items])
        self._ground_truth_info_dict = ground_truth_info_dict
        self._line_counts_dict = line_counts_dict

    def compute_all_metrics_for_all(self):
        for item in self._csv_score_items:
            e_inspect, exam_score = self._compute_literature_metrics_for_csv_item(item)
            metric_val = MetricVal(item.get_experiment_time_seconds(), e_inspect, exam_score)
            item.set_metric_val(metric_val)

    def get_all_csv_score_items(self):
        return self._csv_score_items

    # Call this method after calling compute_all_metrics_for_all.
    def save_all_metrics_for_all(self):
        technique_statement_csv_items = {}
        for item in FLTechnique:
            technique_statement_csv_items[item.name] = self._get_all_csv_items_for(FLTechnique(item.value),
                                                                                   FLGranularity.Statement)

        overall_results_header = ["technique", "experiment_time_seconds", "@1", "@3", "@5", "@10", "exam_score"]
        technique_statement_overall_table = [overall_results_header]
        for technique_name, csv_items in technique_statement_csv_items.items():
            technique_statement_detailed_table = self._get_technique_detailed_results_table(csv_items)
            technique_statement_detailed_file_name = f"detailed_{technique_name}_{FLGranularity.Statement.name}.csv"
            file_manager.save_as_csv_file(technique_statement_detailed_table, technique_statement_detailed_file_name)

            technique_statement_overall_row = self._get_technique_overall_results_row(technique_name, csv_items)
            technique_statement_overall_table.append(technique_statement_overall_row)

        technique_statement_overall_file_name = f"overall_{FLGranularity.Statement.name}.csv"
        file_manager.save_as_csv_file(technique_statement_overall_table, technique_statement_overall_file_name)

    def _compute_e_inspect_for_csv_score_item(self, csv_score_item: CsvScoreItem) -> float:
        bug_key = f"{csv_score_item.get_project_name()}:{csv_score_item.get_bug_number()}"
        bug_ground_truth_dict = self._ground_truth_info_dict[bug_key]
        bug_line_count = self._line_counts_dict[bug_key]
        e_inspect_object = EInspect(csv_score_item.get_scored_entities(), bug_line_count, bug_ground_truth_dict)
        e_inspect_value = e_inspect_object.get_e_inspect()

        return e_inspect_value

    def _compute_exam_score_for_csv_score_item(self, csv_score_item, e_inspect: float) -> float:
        bug_key = f"{csv_score_item.get_project_name()}:{csv_score_item.get_bug_number()}"
        bug_line_count = self._line_counts_dict[bug_key]
        exam_score = e_inspect / bug_line_count

        return exam_score

    def _compute_literature_metrics_for_csv_item(self, csv_score_item) -> Tuple[float, float]:
        e_inspect = self._compute_e_inspect_for_csv_score_item(csv_score_item)
        exam_score = self._compute_exam_score_for_csv_score_item(csv_score_item, e_inspect)
        return e_inspect, exam_score

    def _get_all_csv_items_for(self, tech: FLTechnique, granularity: FLGranularity) -> List[CsvScoreItem]:
        technique_csv_items = []
        for item in self._csv_score_items:
            if item.get_technique() == tech and item.get_granularity() == granularity:
                technique_csv_items.append(item)

        technique_csv_items.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))
        return technique_csv_items

    @staticmethod
    def _get_technique_detailed_results_table(csv_items: List[CsvScoreItem]):
        result_header = ["project_name", "bug_number", "experiment_time_seconds", "e_inspect", "exam_score"]
        result_rows = [result_header]
        for item in csv_items:
            project_name = item.get_project_name()
            bug_number = item.get_bug_number()
            metric_val: MetricVal = item.get_metric_val()
            experiment_time_seconds = metric_val.get_experiment_time()
            assert experiment_time_seconds == item.get_experiment_time_seconds()
            e_inspect = metric_val.get_e_inspect()
            exam_score = metric_val.get_exam_score()
            result_row = [project_name, bug_number, experiment_time_seconds, e_inspect, exam_score]
            result_rows.append(result_row)

        return result_rows

    @staticmethod
    def _get_technique_overall_results_row(technique_name: str,
                                           csv_items: List[CsvScoreItem]) -> List:
        # ["technique", "experiment_time_seconds", "@1", "@3", "@5", "@10", "exam_score"]

        def at_x(top_num: int) -> int:
            top_x_items = list(filter(lambda x: x.get_metric_val().get_e_inspect() <= top_num, csv_items))
            return len(top_x_items)

        def average(nums: List) -> float:
            avg_value = sum(nums) / float(len(nums))
            return avg_value

        experiment_time_seconds_list = [x.get_metric_val().get_experiment_time() for x in csv_items]
        exam_score_list = [x.get_metric_val().get_exam_score() for x in csv_items]

        technique_result = [technique_name,
                            average(experiment_time_seconds_list),
                            at_x(1),
                            at_x(3),
                            at_x(5),
                            at_x(10),
                            average(exam_score_list)]

        return technique_result


class CsvScoreItemLoadManager:
    def __init__(self, results_path: Path):
        self._results_path = results_path

    @classmethod
    def _get_family_csv_score_items(cls, result_path: Path) -> List[CsvScoreItem]:
        technique_statement_csv_score_items = []
        name_parts = result_path.name.split("_")
        script_id = int(name_parts[0])
        project_name = name_parts[3]
        bug_num = int(name_parts[4])
        family = name_parts[5]
        if name_parts[6] == "statement":
            granularity = FLGranularity.Statement
        elif name_parts[6] == "function" and family == "st":
            # We load ST as statement as well
            granularity = FLGranularity.Statement
        else:
            # We are not allowed to have function granularity
            # for other families in the results directory.
            # We compute function granularity from the statement
            # granularity results that we have.
            raise Exception("This should never happen.")

        result_path_dirs = list(filter(lambda x: x.is_dir(), result_path.iterdir()))
        assert len(result_path_dirs) == 1
        fauxpy_result_path = result_path_dirs[0]

        experiment_time_seconds_path = fauxpy_result_path / "deltaTime.txt"
        experiment_time_seconds = cls._extract_experiment_time_seconds_from_file_path(experiment_time_seconds_path)
        assert 0 < experiment_time_seconds <= 48 * 3600  # Less that 48 hours, the cluster server timeout limit.

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
                                             score_table,
                                             experiment_time_seconds)
            technique_statement_csv_score_items.append(current_csv_score)
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
                                                 score_table,
                                                 experiment_time_seconds)
                technique_statement_csv_score_items.append(current_csv_score)

        return technique_statement_csv_score_items

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
        assert granularity == FLGranularity.Statement

        if granularity == FLGranularity.Statement:
            if family in ["sbfl", "mbfl"]:
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_sbfl_mbfl_statement_items(csv_file_content)
            elif family == "ps":
                # TODO: Fix this.
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_ps_statement_items(csv_file_content)
            elif family == "st":
                csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
                scored_entity_items = cls.csv_content_to_scored_st_statement_items(csv_file_content)
            else:
                raise Exception("This should never happen.")
        # elif granularity == FLGranularity.Function:
        #     if family == "ps":
        #         # TODO: Fix this.
        #         csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
        #         scored_entity_items = cls.csv_content_to_scored_function_items(csv_file_content)
        #     else:
        #         csv_file_content = file_manager.load_csv_content_file(csv_paths[0])
        #         scored_entity_items = cls.csv_content_to_scored_function_items(csv_file_content)
        # else:
        #     raise Exception("This should never happen.")

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
    def csv_content_to_scored_st_statement_items(cls,
                                                 csv_file_content: List[List[str]]) -> List[ScoredStatement]:
        scored_statement_items = []
        for row in csv_file_content:
            col1_parts = row[0].split("::")
            file_path_parts = col1_parts[0].split("/")
            relative_file_path = "/".join(file_path_parts[6:])
            line_start = int(col1_parts[2])
            line_end = int(col1_parts[3])
            score = float(row[1])
            for line_number in range(line_start, line_end + 1):
                scored_statement_item = ScoredStatement(relative_file_path, score, line_number)
                scored_statement_items.append(scored_statement_item)

        return scored_statement_items

    # @classmethod
    # def csv_content_to_scored_function_items(cls,
    #                                          csv_file_content: List[List[str]]):
    #     scored_function_items = []
    #     for row in csv_file_content:
    #         col1_parts = row[0].split("::")
    #         file_path_parts = col1_parts[0].split("/")
    #         relative_file_path = "/".join(file_path_parts[6:])
    #         function_name = col1_parts[1]
    #         line_start = int(col1_parts[2])
    #         line_end = int(col1_parts[3])
    #         function_range = (line_start, line_end)
    #         score = float(row[1])
    #         scored_function_item = ScoredFunction(relative_file_path, score, function_range, function_name)
    #         scored_function_items.append(scored_function_item)
    #
    #     return scored_function_items

    @classmethod
    def _extract_experiment_time_seconds_from_file_path(cls, experiment_time_seconds_path):
        file_content = file_manager.load_file_content(experiment_time_seconds_path)
        content_parts = file_content.split("=")
        time_part = content_parts[1].strip()
        num_value_time = float(time_part)
        return num_value_time


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
