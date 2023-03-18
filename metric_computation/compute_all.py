import file_manager
from csv_score_function_granularity_manager import CsvScoreItemFunctionGranularityManager
from csv_score_item_module_granularity_manager import CsvScoreItemModuleGranularityManager
from csv_score_load_manager import CsvScoreItemLoadManager
from result_manager import ResultManager
from timer import Timer


def get_result_manager():
    # result_manager_cache_file_name = "result_manager"
    # result_manager = file_manager.Cache.load(result_manager_cache_file_name)
    # if result_manager is not None:
    #     return result_manager

    path_manager = file_manager.PathManager()

    #  Statement granularity computation
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()
    file_manager.save_score_items_to_given_directory_path(path_manager.get_statement_csv_score_directory_path(),
                                                          statement_csv_score_items)

    #  Function granularity computation
    function_timer = Timer()
    function_timer.startTimer()
    csv_score_item_function_granularity_manager = CsvScoreItemFunctionGranularityManager(statement_csv_score_items,
                                                                                         path_manager.get_workspace_path())
    function_csv_score_items = csv_score_item_function_granularity_manager.get_function_csv_score_items()
    overall_statement_to_function_overhead = function_timer.endTimer()
    file_manager.save_score_items_to_given_directory_path(path_manager.get_function_csv_score_directory_path(),
                                                          function_csv_score_items)
    assert len(statement_csv_score_items) == len(function_csv_score_items)
    # function_csv_score_items = None

    #  Module granularity computation
    module_timer = Timer()
    module_timer.startTimer()
    csv_score_item_module_granularity_manager = CsvScoreItemModuleGranularityManager(statement_csv_score_items)
    module_csv_score_items = csv_score_item_module_granularity_manager.get_module_csv_score_items()
    overall_statement_to_module_overhead = module_timer.endTimer()

    file_manager.save_score_items_to_given_directory_path(path_manager.get_module_csv_score_directory_path(),
                                                          module_csv_score_items)

    assert len(statement_csv_score_items) == len(module_csv_score_items)

    file_manager.save_dictionary_to_json({
        "Statement to function overhead": overall_statement_to_function_overhead,
        "Statement to module overhead": overall_statement_to_module_overhead
    }, path_manager.get_conversion_overhead_file_path())

    ground_truth_info = file_manager.load_json_to_dictionary(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_dictionary(path_manager.get_size_counts_file_name())
    result_manager = ResultManager(statement_csv_score_items,
                                   function_csv_score_items,
                                   module_csv_score_items,
                                   ground_truth_info,
                                   size_counts_info)

    # file_manager.Cache.save(result_manager, result_manager_cache_file_name)

    return result_manager


def main():
    result_manager = get_result_manager()
    result_manager.perform()


if __name__ == '__main__':
    main()
