from typing import Dict, List, Tuple

import mathematics
import our_metrics
from csv_score_load_manager import (FLTechnique,
                                    FLGranularity,
                                    MetricLiteratureVal,
                                    CsvScoreItem,
                                    MetricOurVal)
from literature_metrics import EInspect


class ResultManager:
    def __init__(self,
                 csv_score_items: List[CsvScoreItem],
                 ground_truth_info_dict: Dict,
                 size_counts_dict: Dict):
        self.csv_score_items = csv_score_items
        assert (any([x.get_granularity() == FLGranularity.Statement for x in self.csv_score_items]) or
                any([x.get_granularity() == FLGranularity.Function for x in self.csv_score_items]) or
                any([x.get_granularity() == FLGranularity.Module for x in self.csv_score_items]))
        self._ground_truth_info_dict = ground_truth_info_dict
        self._size_counts_dict = size_counts_dict

    def compute_literature_metrics(self):
        self._compute_all_literature_metrics_for(self.csv_score_items)
        detailed, overall = self._create_all_literature_metrics_for(self.csv_score_items)
        return detailed, overall

    def compute_our_metrics(self):
        # We compute our metrics only for statement granularity.
        assert any([x.get_granularity() == FLGranularity.Statement for x in self.csv_score_items])

        # Our metrics must be computed after literature
        # metrics because we need e_inspect values for our metrics.
        assert any([x.get_metric_literature_val() is not None for x in self.csv_score_items])

        self._compute_all_our_metrics_for_statement_csv_score_items()
        detailed, overall = self._create_all_our_metrics_for_statement_csv_score_items()

        return detailed, overall

    def _compute_all_literature_metrics_for(self, csv_score_items: List[CsvScoreItem]):
        for item in csv_score_items:
            e_inspect, exam_score = self._compute_literature_metrics_for_csv_item(item)
            metric_literature_val = MetricLiteratureVal(item.get_experiment_time_seconds(), e_inspect, exam_score)
            item.set_metric_literature_val(metric_literature_val)

    def _compute_all_our_metrics_for_statement_csv_score_items(self):
        for item in self.csv_score_items:
            e_inspect = item.get_metric_literature_val().get_e_inspect()
            cumulative_distance, sv_comp_overall_score = self._compute_our_metrics(item, e_inspect)
            metric_our_val = MetricOurVal(cumulative_distance, sv_comp_overall_score)
            item.set_metric_our_val(metric_our_val)

    def _create_all_literature_metrics_for(self, csv_score_items: List[CsvScoreItem]):
        technique_csv_items = {}
        for item in FLTechnique:
            technique_csv_items[item.name] = self._get_all_csv_items_for(FLTechnique(item.value),
                                                                         csv_score_items)

        overall_results_header = ["technique", "experiment_time_seconds", "@1", "@1%", "@3", "@3%", "@5", "@5%", "@10",
                                  "@10%", "exam_score"]
        technique_overall_table = [overall_results_header]
        technique_detailed_table_dict = {}
        for technique_name, csv_items in technique_csv_items.items():
            technique_detailed_table = self._get_technique_literature_detailed_results_table(csv_items)
            technique_detailed_table_dict[technique_name] = technique_detailed_table

            technique_overall_row = self._get_technique_literature_overall_results_row(technique_name, csv_items)
            technique_overall_table.append(technique_overall_row)

        return technique_detailed_table_dict, technique_overall_table

    def _create_all_our_metrics_for_statement_csv_score_items(self):
        csv_score_items = self.csv_score_items
        technique_csv_items = {}
        for item in FLTechnique:
            technique_csv_items[item.name] = self._get_all_csv_items_for(FLTechnique(item.value),
                                                                         csv_score_items)

        overall_results_header = ["technique", "cumulative_distance", "sv_comp_overall_score"]
        technique_overall_table = [overall_results_header]
        technique_detailed_table_dict = {}
        for technique_name, csv_items in technique_csv_items.items():
            technique_detailed_table = self._get_technique_our_detailed_results_table(csv_items)
            technique_detailed_table_dict[technique_name] = technique_detailed_table

            technique_overall_row = self._get_technique_our_overall_results_row(technique_name, csv_items)
            technique_overall_table.append(technique_overall_row)

        return technique_detailed_table_dict, technique_overall_table

    def _compute_e_inspect_for_csv_score_item(self, csv_score_item: CsvScoreItem) -> float:
        bug_key = csv_score_item.get_bug_key()
        if csv_score_item.get_granularity() == FLGranularity.Statement:
            bug_line_count = self._size_counts_dict[bug_key]["LINE_COUNT"]
            buggy_lines_list, _ = self._get_ground_truth_buggy_line_names_and_module_size_dict(bug_key)
            assert len(buggy_lines_list) > 0
            e_inspect_object = EInspect(csv_score_item.get_scored_entities(),
                                        bug_line_count,
                                        buggy_lines_list)
            e_inspect_value = e_inspect_object.get_e_inspect()
        elif csv_score_item.get_granularity() == FLGranularity.Function:
            function_count = self._size_counts_dict[bug_key]["FUNCTION_COUNT"]
            buggy_functions_list = self._get_ground_truth_buggy_function_names(bug_key)
            if len(buggy_functions_list) == 0:
                # If none of buggy lines in the ground truth
                # info are functions, E_Inspect is the number
                # of functions within the source code because
                # the technique cannot find it and the user has to
                # go through all functions.
                # This one does not happen for statement granularity
                # as we have already removed buggy versions with
                # empty ground truths.
                e_inspect_value = function_count
            else:
                e_inspect_object = EInspect(csv_score_item.get_scored_entities(),
                                            function_count,
                                            buggy_functions_list)
                e_inspect_value = e_inspect_object.get_e_inspect()
        elif csv_score_item.get_granularity() == FLGranularity.Module:
            module_count = self._size_counts_dict[bug_key]["MODULE_COUNT"]
            buggy_module_list = self._get_ground_truth_buggy_module_names(bug_key)
            assert len(buggy_module_list) > 0
            e_inspect_object = EInspect(csv_score_item.get_scored_entities(),
                                        module_count,
                                        buggy_module_list)
            e_inspect_value = e_inspect_object.get_e_inspect()
        else:
            raise Exception()

        return e_inspect_value

    def _compute_exam_score_for_csv_score_item(self, csv_score_item: CsvScoreItem, e_inspect: float) -> float:
        bug_key = csv_score_item.get_bug_key()
        if csv_score_item.get_granularity() == FLGranularity.Statement:
            entity_count_in_project = self._size_counts_dict[bug_key]["LINE_COUNT"]
        elif csv_score_item.get_granularity() == FLGranularity.Function:
            entity_count_in_project = self._size_counts_dict[bug_key]["FUNCTION_COUNT"]
        elif csv_score_item.get_granularity() == FLGranularity.Module:
            entity_count_in_project = self._size_counts_dict[bug_key]["MODULE_COUNT"]
        else:
            raise Exception()

        exam_score = e_inspect / entity_count_in_project
        return exam_score

    def _compute_literature_metrics_for_csv_item(self, csv_score_item: CsvScoreItem) -> Tuple[float, float]:
        e_inspect = self._compute_e_inspect_for_csv_score_item(csv_score_item)
        exam_score = self._compute_exam_score_for_csv_score_item(csv_score_item, e_inspect)
        return e_inspect, exam_score

    @staticmethod
    def _get_all_csv_items_for(tech: FLTechnique,
                               csv_score_items: List[CsvScoreItem]) -> List[CsvScoreItem]:
        technique_csv_items = []
        for item in csv_score_items:
            if item.get_technique() == tech:
                technique_csv_items.append(item)

        technique_csv_items.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))
        return technique_csv_items

    @staticmethod
    def _get_technique_literature_detailed_results_table(csv_items: List[CsvScoreItem]):
        result_header = ["project_name", "bug_number", "experiment_time_seconds", "e_inspect", "exam_score"]
        result_rows = [result_header]
        for item in csv_items:
            project_name = item.get_project_name()
            bug_number = item.get_bug_number()
            metric_val: MetricLiteratureVal = item.get_metric_literature_val()
            experiment_time_seconds = metric_val.get_experiment_time()
            assert experiment_time_seconds == item.get_experiment_time_seconds()
            e_inspect = metric_val.get_e_inspect()
            exam_score = metric_val.get_exam_score()
            result_row = [project_name, bug_number, experiment_time_seconds, e_inspect, exam_score]
            result_rows.append(result_row)

        return result_rows

    @staticmethod
    def _get_technique_our_detailed_results_table(csv_items: List[CsvScoreItem]):
        result_header = ["project_name", "bug_number", "cumulative_distance", "sv_comp_overall_score"]
        result_rows = [result_header]
        for item in csv_items:
            project_name = item.get_project_name()
            bug_number = item.get_bug_number()
            metric_val = item.get_metric_our_val()
            cumulative_distance = metric_val.get_cumulative_distance()
            sv_comp_overall_score = metric_val.get_sv_comp_overall_score()
            result_row = [project_name, bug_number, cumulative_distance, sv_comp_overall_score]
            result_rows.append(result_row)

        return result_rows

    @staticmethod
    def _get_technique_literature_overall_results_row(technique_name: str,
                                                      csv_items: List[CsvScoreItem]) -> List:
        # ["technique", "experiment_time_seconds", "@1", "@1%", "@3", "@3%", "@5", "@5%", "@10", "@10%", "exam_score"]

        if len(csv_items) == 0:
            return [None, None, None, None, None, None, None, None, None, None, None]

        def at_x(top_num: int) -> int:
            top_x_items = list(filter(lambda x: x.get_metric_literature_val().get_e_inspect() <= top_num, csv_items))
            return len(top_x_items)

        def at_x_percentage(top_num: int) -> float:
            percentage = (float(at_x(top_num)) / len(csv_items)) * 100
            round_percentage = round(percentage)
            return round_percentage

        experiment_time_seconds_list = [x.get_metric_literature_val().get_experiment_time() for x in csv_items]
        exam_score_list = [x.get_metric_literature_val().get_exam_score() for x in csv_items]

        average_experiment_time = mathematics.average(experiment_time_seconds_list)
        round_average_experiment_time = round(average_experiment_time)

        average_exam_score = mathematics.average(exam_score_list)
        round_average_exam_score = round(average_exam_score, 3)

        technique_result = [technique_name,
                            round_average_experiment_time,
                            at_x(1),
                            at_x_percentage(1),
                            at_x(3),
                            at_x_percentage(3),
                            at_x(5),
                            at_x_percentage(5),
                            at_x(10),
                            at_x_percentage(10),
                            round_average_exam_score]

        return technique_result

    @staticmethod
    def _get_technique_our_overall_results_row(technique_name: str,
                                               csv_items: List[CsvScoreItem]) -> List:
        # ["technique", "cumulative_distance", "sv_comp_overall_score"]

        if len(csv_items) == 0:
            return [None, None, None]

        cumulative_distance_list = [x.get_metric_our_val().get_cumulative_distance() for x in csv_items]
        average_cumulative_distance = mathematics.average(cumulative_distance_list)
        # round_average_cumulative_distance = round(average_cumulative_distance)

        sv_comp_overall_score_list = [x.get_metric_our_val().get_sv_comp_overall_score() for x in csv_items]
        average_sv_comp_overall_score = mathematics.average(sv_comp_overall_score_list)
        # round_average_sv_comp_overall_score = round(average_sv_comp_overall_score)

        technique_result = [technique_name,
                            average_cumulative_distance,
                            average_sv_comp_overall_score]

        return technique_result

    def _get_ground_truth_buggy_line_names_and_module_size_dict(self, bug_key: str) -> Tuple[List[str], Dict[str, int]]:
        buggy_entity_names = []
        buggy_module_sizes = {}
        bug_ground_truth = self._ground_truth_info_dict[bug_key]
        for module_item in bug_ground_truth:
            module_name = module_item["FILE_NAME"]
            entity_items = module_item["LINES"] + module_item["EXTENDED_LINES"]
            module_size = module_item["MODULE_SIZE"]
            buggy_module_sizes[module_name] = module_size
            for entity_item in entity_items:
                entity_name = f"{module_name}::{entity_item}"
                buggy_entity_names.append(entity_name)

        return buggy_entity_names, buggy_module_sizes

    def _get_ground_truth_buggy_function_names(self, bug_key: str) -> List[str]:
        buggy_entity_names = []
        bug_ground_truth = self._ground_truth_info_dict[bug_key]
        for module_item in bug_ground_truth:
            module_name = module_item["FILE_NAME"]
            entity_items = module_item["FUNCTIONS"] + module_item["EXTENDED_FUNCTIONS"]
            for entity_item in entity_items:
                entity_name = f"{module_name}::{entity_item}"
                buggy_entity_names.append(entity_name)

        return buggy_entity_names

    def _get_ground_truth_buggy_module_names(self, bug_key: str) -> List[str]:
        buggy_entity_names = []
        bug_ground_truth = self._ground_truth_info_dict[bug_key]
        for module_item in bug_ground_truth:
            module_name = module_item["FILE_NAME"]
            buggy_entity_names.append(module_name)

        return buggy_entity_names

    def _compute_our_metrics(self,
                             csv_score_item: CsvScoreItem,
                             e_inspect: float):
        bug_key = csv_score_item.get_bug_key()
        ground_truth_buggy_line_names, buggy_module_sizes = self._get_ground_truth_buggy_line_names_and_module_size_dict(
            bug_key)
        cumulative_distance = our_metrics.get_cumulative_distance(csv_score_item.get_scored_entities(),
                                                                  ground_truth_buggy_line_names,
                                                                  buggy_module_sizes,
                                                                  e_inspect)

        sv_comp_overall_score = our_metrics.get_sv_comp_overall_score(csv_score_item.get_scored_entities(),
                                                                      ground_truth_buggy_line_names,
                                                                      buggy_module_sizes,
                                                                      e_inspect)
        return cumulative_distance, sv_comp_overall_score
