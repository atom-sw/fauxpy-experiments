import copy
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
                 size_counts_dict: Dict,
                 our_metric=False):
        self._csv_score_items = csv_score_items
        assert (any([x.get_granularity() == FLGranularity.Statement for x in self._csv_score_items]) or
                any([x.get_granularity() == FLGranularity.Function for x in self._csv_score_items]) or
                any([x.get_granularity() == FLGranularity.Module for x in self._csv_score_items]))
        self._our_metric = our_metric
        assert not self._our_metric or (self._our_metric and
                                        any([x.get_granularity() == FLGranularity.Statement for x in
                                             self._csv_score_items]))
        self._ground_truth_info_dict = ground_truth_info_dict
        self._size_counts_dict = size_counts_dict
        self._all_techniques = self._get_all_techniques()
        assert (any([x.get_is_crashing() is not None and x.get_is_predicate() is not None for x in self._csv_score_items]))

    def _get_all_techniques(self):
        all_techniques = set()
        for csv_score_item in self._csv_score_items:
            all_techniques.add(csv_score_item.get_technique())
        all_techniques_list = list(all_techniques)
        all_techniques_list.sort(key=lambda x: x.value)

        return all_techniques_list

    def get_metric_results(self):
        self._compute_all_literature_metrics_for(self._csv_score_items)
        literature_detailed, literature_overall = self._create_all_literature_metrics_for(self._csv_score_items)
        if not self._our_metric:
            our_detailed, our_overall = self._get_empty_our_metric_results()
        else:
            our_detailed, our_overall = self._get_our_metric_results()

        all_detailed, all_overall = self._combine_literature_with_our_metrics(literature_detailed,
                                                                              literature_overall,
                                                                              our_detailed,
                                                                              our_overall)
        all_detailed_for_all_techniques = self._combine_all_detailed_of_techniques_in_one_list(all_detailed)
        return all_detailed_for_all_techniques, all_overall

    def get_score_based_quantile_function(self) -> List[List]:
        self._check_if_our_metric_applicable()

        # Score-based quantile function must be computed
        # after our other two metrics are computed.
        assert any([x.get_metric_our_val() is not None for x in self._csv_score_items])

        all_quantiles_table = []
        all_quantiles_header = ["time", "technique", "sum_of_all_positive_scores"]
        all_quantiles_table.append(all_quantiles_header)
        for technique in self._all_techniques:
            technique_csv_score_items = self._get_all_csv_items_for(technique, self._csv_score_items)
            technique_quantile_records = our_metrics.score_based_quantile_function_for_technique(technique_csv_score_items)
            all_quantiles_table += [x.get_record() for x in technique_quantile_records]

        return all_quantiles_table

    def _get_our_metric_results(self):
        self._check_if_our_metric_applicable()

        self._compute_all_our_metrics_for_statement_csv_score_items()
        detailed, overall = self._create_all_our_metrics_for_statement_csv_score_items()

        return detailed, overall

    def _get_empty_our_metric_results(self):
        def get_empty_technique_our_detailed_results_table(csv_item_list: List[CsvScoreItem]):
            result_header = ["project_name", "bug_number", "cumulative_distance", "sv_comp_overall_score"]
            result_rows = [result_header]
            for csv_item in csv_item_list:
                project_name = csv_item.get_project_name()
                bug_number = csv_item.get_bug_number()
                cumulative_distance = None
                sv_comp_overall_score = None
                result_row = [project_name, bug_number, cumulative_distance, sv_comp_overall_score]
                result_rows.append(result_row)
            return result_rows

        def get_empty_technique_our_overall_results_row(tech: str,
                                                        csv_item_list: List[CsvScoreItem]) -> List:
            # ["technique", "cumulative_distance", "sv_comp_overall_score"]

            if len(csv_items) == 0:
                return [None, None, None]

            average_cumulative_distance = None
            average_sv_comp_overall_score = None

            technique_result = [tech,
                                average_cumulative_distance,
                                average_sv_comp_overall_score]

            return technique_result

        csv_score_items = self._csv_score_items
        technique_csv_items = {}
        for item in self._all_techniques:
            technique_csv_items[item.name] = self._get_all_csv_items_for(FLTechnique(item.value),
                                                                         csv_score_items)

        overall_results_header = ["technique", "cumulative_distance", "sv_comp_overall_score"]
        technique_overall_table = [overall_results_header]
        technique_detailed_table_dict = {}
        for technique_name, csv_items in technique_csv_items.items():
            technique_detailed_table = get_empty_technique_our_detailed_results_table(csv_items)
            technique_detailed_table_dict[technique_name] = technique_detailed_table

            technique_overall_row = get_empty_technique_our_overall_results_row(technique_name, csv_items)
            technique_overall_table.append(technique_overall_row)

        return technique_detailed_table_dict, technique_overall_table

    def _compute_all_literature_metrics_for(self, csv_score_items: List[CsvScoreItem]):
        for item in csv_score_items:
            e_inspect, exam_score = self._compute_literature_metrics_for_csv_item(item)
            metric_literature_val = MetricLiteratureVal(item.get_experiment_time_seconds(), e_inspect, exam_score)
            item.set_metric_literature_val(metric_literature_val)

    def _compute_all_our_metrics_for_statement_csv_score_items(self):
        for item in self._csv_score_items:
            e_inspect = item.get_metric_literature_val().get_e_inspect()
            cumulative_distance, sv_comp_overall_score = self._compute_our_metrics(item, e_inspect)
            metric_our_val = MetricOurVal(cumulative_distance, sv_comp_overall_score)
            item.set_metric_our_val(metric_our_val)

    def _create_all_literature_metrics_for(self, csv_score_items: List[CsvScoreItem]):
        technique_csv_items = {}
        for item in self._all_techniques:
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
        csv_score_items = self._csv_score_items
        technique_csv_items = {}
        for item in self._all_techniques:
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

    @classmethod
    def _get_technique_literature_detailed_results_table(cls, csv_items: List[CsvScoreItem]):
        result_header = ["project_name", "bug_number", "granularity", "technique", "crashing", "predicate", "mutable_bug",
                         "experiment_time_seconds", "e_inspect", "exam_score"]
        result_rows = [result_header]
        for item in csv_items:
            project_name = item.get_project_name()
            bug_number = item.get_bug_number()
            granularity_name = item.get_granularity().name
            technique_name = item.get_technique().name
            crashing = cls._bool_to_int(item.get_is_crashing())
            predicate = cls._bool_to_int(item.get_is_predicate())
            mutable_bug = cls._bool_to_int(item.get_is_mutable_bug())
            metric_val: MetricLiteratureVal = item.get_metric_literature_val()
            experiment_time_seconds = metric_val.get_experiment_time()
            assert experiment_time_seconds == item.get_experiment_time_seconds()
            e_inspect = metric_val.get_e_inspect()
            exam_score = metric_val.get_exam_score()
            result_row = [project_name, bug_number, granularity_name, technique_name, crashing, predicate, mutable_bug,
                          experiment_time_seconds, e_inspect, exam_score]
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

    @staticmethod
    def _combine_literature_with_our_metrics(literature_detailed,
                                             literature_overall,
                                             our_detailed,
                                             our_overall) -> Tuple[Dict, List]:
        assert len(literature_detailed) == len(our_detailed)
        assert len(literature_overall) == len(our_overall)

        all_detailed = {}
        for lit_d_technique, lit_d_table in literature_detailed.items():
            our_d_table = our_detailed[lit_d_technique]
            assert len(lit_d_table) == len(our_d_table)
            current_d_table = []
            for index, lit_d_record in enumerate(lit_d_table):
                our_d_record = our_d_table[index]
                assert lit_d_record[0] == our_d_record[0]
                assert lit_d_record[1] == our_d_record[1]
                current_d_record = copy.copy(lit_d_record) + copy.copy(our_d_record[2:])
                current_d_table.append(current_d_record)
            all_detailed[lit_d_technique] = current_d_table

        assert len(literature_detailed) == len(all_detailed)

        all_overall = []
        for index, lit_o_record in enumerate(literature_overall):
            our_o_record = our_overall[index]
            assert lit_o_record[0] == our_o_record[0]
            current_o_record = copy.copy(lit_o_record) + copy.copy(our_o_record[1:])
            all_overall.append(current_o_record)

        assert len(literature_overall) == len(all_overall)

        return all_detailed, all_overall

    @staticmethod
    def _bool_to_int(value: bool) -> int:
        if value:
            return 1
        else:
            return 0

    @staticmethod
    def _combine_all_detailed_of_techniques_in_one_list(all_detailed: Dict):
        combined_all_details = []
        detailed_header = list(all_detailed.values())[0][0]
        combined_all_details.append(detailed_header)
        for technique, technique_detailed_table in all_detailed.items():
            assert any([x[3] == technique for x in technique_detailed_table[1:]])
            combined_all_details += technique_detailed_table[1:]

        return combined_all_details

    def _check_if_our_metric_applicable(self):
        # We compute our metrics only for statement granularity.
        assert any([x.get_granularity() == FLGranularity.Statement for x in self._csv_score_items])

        # Our metrics must be computed after literature
        # metrics because we need e_inspect values for our metrics.
        assert any([x.get_metric_literature_val() is not None for x in self._csv_score_items])
