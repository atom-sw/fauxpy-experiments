import file_manager
from csv_score_function_granularity_manager import CsvScoreItemFunctionGranularityManager
from csv_score_item_module_granularity_manager import CsvScoreItemModuleGranularityManager
from csv_score_load_manager import CsvScoreItemLoadManager
from result_manager import ResultManager


def get_fauxpy_statement_csv_score_items(path_manager: file_manager.PathManager):
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()

    return statement_csv_score_items


def convert_statement_csv_to_function_csv(path_manager, fauxpy_statement_csv_score_items):
    csv_score_item_function_granularity_manager = CsvScoreItemFunctionGranularityManager(
        fauxpy_statement_csv_score_items,
        path_manager.get_workspace_path())
    fauxpy_function_csv_score_items = csv_score_item_function_granularity_manager.get_function_csv_score_items()

    return fauxpy_function_csv_score_items


def convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items):
    csv_score_item_module_granularity_manager = CsvScoreItemModuleGranularityManager(fauxpy_statement_csv_score_items)
    module_csv_score_items = csv_score_item_module_granularity_manager.get_module_csv_score_items()

    return module_csv_score_items


def save_detailed(detailed_tables, metric_type, dir_name):
    for technique_name, results_table in detailed_tables.items():
        technique_detailed_file_name = f"{metric_type}_detailed_{technique_name}.csv"
        file_manager.save_csv_to_output_dir(results_table,
                                            dir_name,
                                            technique_detailed_file_name)


def save_overall(overall_table, metric_type, dir_name):
    technique_overall_file_name = f"{metric_type}_overall.csv"
    file_manager.save_csv_to_output_dir(overall_table,
                                        dir_name,
                                        technique_overall_file_name)


def calc_fauxpy_statement_and_save(fauxpy_statement_csv_score_items, ground_truth_info, size_counts_info):
    fauxpy_statement_result_manager = ResultManager(fauxpy_statement_csv_score_items,
                                                    ground_truth_info,
                                                    size_counts_info)
    literature_detailed_tables, literature_overall_table = fauxpy_statement_result_manager.compute_literature_metrics()
    dir_name = "output_fauxpy_statement"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(literature_detailed_tables, "literature", dir_name)
    save_overall(literature_overall_table, "literature", dir_name)
    our_detailed_tables, our_overall_table = fauxpy_statement_result_manager.compute_our_metrics()
    save_detailed(our_detailed_tables, "our", dir_name)
    save_overall(our_overall_table, "our", dir_name)


def calc_fauxpy_function_and_save(fauxpy_function_csv_score_items, ground_truth_info, size_counts_info):
    fauxpy_result_manager = ResultManager(fauxpy_function_csv_score_items,
                                          ground_truth_info,
                                          size_counts_info)
    literature_detailed_tables, literature_overall_table = fauxpy_result_manager.compute_literature_metrics()
    dir_name = "output_fauxpy_function"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(literature_detailed_tables, "literature", dir_name)
    save_overall(literature_overall_table, "literature", dir_name)


def calc_fauxpy_module_and_save(fauxpy_module_csv_score_items, ground_truth_info, size_counts_info):
    fauxpy_result_manager = ResultManager(fauxpy_module_csv_score_items,
                                          ground_truth_info,
                                          size_counts_info)
    literature_detailed_tables, literature_overall_table = fauxpy_result_manager.compute_literature_metrics()
    dir_name = "output_fauxpy_module"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(literature_detailed_tables, "literature", dir_name)
    save_overall(literature_overall_table, "literature", dir_name)


def main():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_dictionary(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_dictionary(path_manager.get_size_counts_file_name())
    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    file_manager.save_score_items_to_given_directory_path(path_manager.get_statement_csv_score_directory_path(),
                                                          fauxpy_statement_csv_score_items)

    calc_fauxpy_statement_and_save(fauxpy_statement_csv_score_items, ground_truth_info, size_counts_info)

    fauxpy_function_csv_score_items = convert_statement_csv_to_function_csv(path_manager,
                                                                            fauxpy_statement_csv_score_items)

    file_manager.save_score_items_to_given_directory_path(path_manager.get_function_csv_score_directory_path(),
                                                          fauxpy_function_csv_score_items)

    calc_fauxpy_function_and_save(fauxpy_function_csv_score_items, ground_truth_info, size_counts_info)

    fauxpy_module_csv_score_items = convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items)

    file_manager.save_score_items_to_given_directory_path(path_manager.get_module_csv_score_directory_path(),
                                                          fauxpy_module_csv_score_items)

    calc_fauxpy_module_and_save(fauxpy_module_csv_score_items, ground_truth_info, size_counts_info)


if __name__ == '__main__':
    main()
