from typing import Dict, List, Tuple

import file_manager
import mathematics
from csv_score_function_granularity_manager import CsvScoreItemFunctionGranularityManager
from csv_score_load_manager import CsvScoreItemLoadManager, FLTechnique, FLGranularity, MetricVal, CsvScoreItem
from literature_metrics import EInspect


class ResultManager:
    def __init__(self,
                 statement_csv_score_items: List[CsvScoreItem],
                 function_csv_score_items: List[CsvScoreItem],
                 ground_truth_info_dict: Dict,
                 line_counts_dict: Dict):
        self._statement_csv_score_items = statement_csv_score_items
        self._function_csv_score_items = function_csv_score_items
        assert any([x.get_granularity() == FLGranularity.Statement for x in self._statement_csv_score_items])
        self._ground_truth_info_dict = ground_truth_info_dict
        self._line_counts_dict = line_counts_dict

    def compute_all_metrics_for_all(self):
        for item in self._statement_csv_score_items:
            e_inspect, exam_score = self._compute_literature_metrics_for_csv_item(item)
            metric_val = MetricVal(item.get_experiment_time_seconds(), e_inspect, exam_score)
            item.set_metric_val(metric_val)

    def get_all_csv_score_items(self):
        return self._statement_csv_score_items

    # Call this method after calling compute_all_metrics_for_all.
    def save_all_metrics_for_all(self):
        technique_statement_csv_items = {}
        for item in FLTechnique:
            technique_statement_csv_items[item.name] = self._get_all_csv_items_for(FLTechnique(item.value),
                                                                                   FLGranularity.Statement)

        overall_results_header = ["technique", "experiment_time_seconds", "@1", "@1%", "@3", "@3%", "@5", "@5%", "@10",
                                  "@10%", "exam_score"]
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
        for item in self._statement_csv_score_items:
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
        # ["technique", "experiment_time_seconds", "@1", "@1%", "@3", "@3%", "@5", "@5%", "@10", "@10%", "exam_score"]

        def at_x(top_num: int) -> int:
            top_x_items = list(filter(lambda x: x.get_metric_val().get_e_inspect() <= top_num, csv_items))
            return len(top_x_items)

        def at_x_percentage(top_num: int) -> float:
            percentage = (float(at_x(top_num)) / len(csv_items)) * 100
            return percentage

        experiment_time_seconds_list = [x.get_metric_val().get_experiment_time() for x in csv_items]
        exam_score_list = [x.get_metric_val().get_exam_score() for x in csv_items]

        technique_result = [technique_name,
                            mathematics.average(experiment_time_seconds_list),
                            at_x(1),
                            at_x_percentage(1),
                            at_x(3),
                            at_x_percentage(3),
                            at_x(5),
                            at_x_percentage(5),
                            at_x(10),
                            at_x_percentage(10),
                            mathematics.average(exam_score_list)]

        return technique_result


def get_result_manager():
    path_manager = file_manager.PathManager()
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()

    csv_score_item_function_granularity_manager = CsvScoreItemFunctionGranularityManager(statement_csv_score_items)
    function_csv_score_items = csv_score_item_function_granularity_manager.get_function_csv_score_items()

    ground_truth_info = file_manager.load_json_to_dictionary(path_manager.get_ground_truth_path())
    line_counts_info = file_manager.load_json_to_dictionary(path_manager.get_line_counts_path())
    result_manager = ResultManager(statement_csv_score_items,
                                   function_csv_score_items,
                                   ground_truth_info,
                                   line_counts_info)

    return result_manager
