from pathlib import Path
from typing import List, Dict, Tuple

from tqdm import tqdm

import file_manager
import latex_inf_generator_tool_demo
import mathematics
from average_fault_localization import AverageFaultLocalization
from combine_fl_manager import CombineFlManager
from csv_score_function_granularity_manager import CsvScoreItemFunctionGranularityManager
from csv_score_item_module_granularity_manager import CsvScoreItemModuleGranularityManager
from csv_score_load_manager import CsvScoreItemLoadManager, FLTechnique, ProjectType, CsvScoreItem, FLGranularity
from hierarchical_fault_localization import HierarchicalFaultLocalization
from latex_info_generator import LatexInfo
from result_manager import ResultManager
from selected_bugs_types import assign_type_to_selected_bugs


def are_all_different_in_list(item_list) -> bool:
    if len(item_list) == 0:
        return False

    for index_1 in range(0, len(item_list)):
        for index_2 in range(index_1 + 1, len(item_list)):
            if item_list[index_1] == item_list[index_2]:
                return False

    return True


def get_non_empty_critical_predicate_csv_items(fauxpy_statement_csv_score_items):
    non_empty_ps_csv_items = [x for x in fauxpy_statement_csv_score_items
                              if x.get_technique() == FLTechnique.PS and
                              len(x.get_scored_entities()) != 0]
    non_empty_ps_csv_items.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))
    non_empty_ps_bug_key_list = [x.get_bug_key() for x in non_empty_ps_csv_items]

    non_empty_critical_predicate_csv_items_list = [x for x in fauxpy_statement_csv_score_items
                                                   if x.get_bug_key() in non_empty_ps_bug_key_list]

    return non_empty_critical_predicate_csv_items_list


def get_fauxpy_statement_csv_score_items(path_manager: file_manager.PathManager):
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()

    assign_type_to_selected_bugs(statement_csv_score_items, path_manager)

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


def get_mfs_hfl_statement_csv_score_items(fauxpy_statement_csv_score_items,
                                          fauxpy_function_csv_score_items,
                                          fauxpy_module_csv_score_items):
    mfs_hfl_statement_csv_score_items = []
    for index in range(0, len(fauxpy_statement_csv_score_items)):
        print(fauxpy_statement_csv_score_items[index].get_bug_key())
        mfs_hfl = HierarchicalFaultLocalization(
            fauxpy_statement_csv_score_items[index],
            fauxpy_function_csv_score_items[index],
            fauxpy_module_csv_score_items[index])
        current_statement_csv_score_item = mfs_hfl.get_mfs_hfl_statement_csv_score_item()
        mfs_hfl_statement_csv_score_items.append(current_statement_csv_score_item)

    return mfs_hfl_statement_csv_score_items


def get_fs_hfl_statement_csv_score_items(fauxpy_statement_csv_score_items,
                                         fauxpy_function_csv_score_items,
                                         fauxpy_module_csv_score_items):
    fs_hfl_statement_csv_score_items = []
    for index in range(0, len(fauxpy_statement_csv_score_items)):
        print(fauxpy_statement_csv_score_items[index].get_bug_key())
        fs_hfl = HierarchicalFaultLocalization(
            fauxpy_statement_csv_score_items[index],
            fauxpy_function_csv_score_items[index],
            fauxpy_module_csv_score_items[index])
        current_statement_csv_score_item = fs_hfl.get_fs_hfl_statement_csv_score_item()
        fs_hfl_statement_csv_score_items.append(current_statement_csv_score_item)

    return fs_hfl_statement_csv_score_items


def get_avg_csv_score_items(fauxpy_csv_score_items, tech_name: FLTechnique):
    def get_csv_technique(technique: FLTechnique, bug_key: str):
        technique_csv = list(filter(lambda x:
                                    (x.get_technique() == technique and
                                     x.get_bug_key() == bug_key),
                                    fauxpy_csv_score_items))[0]
        return technique_csv

    average_fl_csv_score_item_list = []

    all_ochiai_csv_list = list(
        filter(lambda x: x.get_technique() == FLTechnique.Ochiai, fauxpy_csv_score_items))
    for ochiai_csv in tqdm(all_ochiai_csv_list):
        print("\n" + ochiai_csv.get_bug_key())
        dstar_csv = get_csv_technique(FLTechnique.DStar, ochiai_csv.get_bug_key())
        st_csv = get_csv_technique(FLTechnique.ST, ochiai_csv.get_bug_key())
        techniques_csv_list = [
            ochiai_csv,
            dstar_csv,
            st_csv
        ]

        if tech_name == FLTechnique.AvgAlfa:
            metallaxis_csv = get_csv_technique(FLTechnique.Metallaxis, ochiai_csv.get_bug_key())
            muse_csv = get_csv_technique(FLTechnique.Muse, ochiai_csv.get_bug_key())
            ps_csv = get_csv_technique(FLTechnique.PS, ochiai_csv.get_bug_key())
            techniques_csv_list += [
                metallaxis_csv,
                muse_csv,
                ps_csv,
            ]

        average_fl = AverageFaultLocalization(techniques_csv_list, tech_name)
        average_fl_csv_score_item = average_fl.get_average_fl_csv_score_item()
        average_fl_csv_score_item_list.append(average_fl_csv_score_item)

    return average_fl_csv_score_item_list


def save_detailed(detailed_table: List, tool_name: str, granularity: str, bug_type: str, dir_name: str):
    technique_detailed_file_name = f"{tool_name}_{granularity}_{bug_type}_detailed.csv"
    file_manager.save_csv_to_output_dir(detailed_table,
                                        dir_name,
                                        technique_detailed_file_name)


def save_overall(overall_table: List, tool_name: str, granularity: str, bug_type: str, dir_name: str):
    technique_overall_file_name = f"{tool_name}_{granularity}_{bug_type}_overall.csv"
    file_manager.save_csv_to_output_dir(overall_table,
                                        dir_name,
                                        technique_overall_file_name)


def save_latex_info(overall_table: List, tool_name: str, granularity: str, bug_type: str):
    path_manager = file_manager.PathManager()
    latex_dir_path = file_manager.make_if_not_dir(path_manager.get_latex_table_dir_name())
    technique_overall_file_name = f"{tool_name}_{granularity}_{bug_type}_overall.json"
    file_path = latex_dir_path / technique_overall_file_name
    file_manager.save_object_to_json(overall_table, file_path)


def save_quantile(overall_table: List, tool_name: str, granularity: str, bug_type: str, dir_name: str):
    quantile_file_name = f"{tool_name}_{granularity}_{bug_type}_quantile.csv"
    file_manager.save_csv_to_output_dir(overall_table,
                                        dir_name,
                                        quantile_file_name)


def calc_fauxpy_statement_and_save(fauxpy_statement_csv_score_items, ground_truth_info, size_counts_info):
    def compute_metrics(csv_items, bug_type):
        fauxpy_statement_result_manager = ResultManager(csv_items,
                                                        ground_truth_info,
                                                        size_counts_info,
                                                        True)
        all_detailed_tables, all_overall_table = fauxpy_statement_result_manager.get_metric_results()
        all_quantiles = fauxpy_statement_result_manager.get_score_based_quantile_function()
        save_detailed(all_detailed_tables, "fauxpy", "statement", bug_type, dir_name)
        save_overall(all_overall_table, "fauxpy", "statement", bug_type, dir_name)
        save_quantile(all_quantiles, "fauxpy", "statement", bug_type, dir_name)
        save_latex_info(all_overall_table, "fauxpy", "statement", bug_type)

    dir_name = "output_fauxpy_statement"
    file_manager.clean_make_output_dir(dir_name)

    predicate_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_is_predicate()]
    crashing_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_is_crashing()]
    mutable_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_is_mutable_bug()]
    # non_empty_critical_predicate_csv_items = get_non_empty_critical_predicate_csv_items(
    #     fauxpy_statement_csv_score_items)

    dev_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_project_type() == ProjectType.Dev]
    ds_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_project_type() == ProjectType.DS]
    web_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_project_type() == ProjectType.Web]
    cli_csv_items = [x for x in fauxpy_statement_csv_score_items if x.get_project_type() == ProjectType.CLI]

    compute_metrics(fauxpy_statement_csv_score_items, "all")
    compute_metrics(predicate_csv_items, "predicate")
    compute_metrics(crashing_csv_items, "crashing")
    compute_metrics(mutable_csv_items, "mutable")
    # compute_metrics(non_empty_critical_predicate_csv_items, "non-empty-critical-predicate")

    compute_metrics(dev_csv_items, "dev")
    compute_metrics(ds_csv_items, "ds")
    compute_metrics(web_csv_items, "web")
    compute_metrics(cli_csv_items, "cli")


def calc_fauxpy_function_and_save(fauxpy_function_csv_score_items, ground_truth_info, size_counts_info):
    fauxpy_result_manager = ResultManager(fauxpy_function_csv_score_items,
                                          ground_truth_info,
                                          size_counts_info)
    all_detailed_tables, all_overall_table = fauxpy_result_manager.get_metric_results()
    dir_name = "output_fauxpy_function"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(all_detailed_tables, "fauxpy", "function", "all", dir_name)
    save_overall(all_overall_table, "fauxpy", "function", "all", dir_name)

    save_latex_info(all_overall_table, "fauxpy", "function", "all")


def calc_fauxpy_module_and_save(fauxpy_module_csv_score_items, ground_truth_info, size_counts_info):
    fauxpy_result_manager = ResultManager(fauxpy_module_csv_score_items,
                                          ground_truth_info,
                                          size_counts_info)
    all_detailed_tables, all_overall_table = fauxpy_result_manager.get_metric_results()
    dir_name = "output_fauxpy_module"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(all_detailed_tables, "fauxpy", "module", "all", dir_name)
    save_overall(all_overall_table, "fauxpy", "module", "all", dir_name)

    save_latex_info(all_overall_table, "fauxpy", "module", "all")


def calc_mfs_hfl_statement_and_save(mfs_hfl_statement_csv_score_items, ground_truth_info, size_counts_info):
    mfs_hfl_statement_result_manager = ResultManager(mfs_hfl_statement_csv_score_items,
                                                     ground_truth_info,
                                                     size_counts_info,
                                                     True)
    literature_detailed_tables, literature_overall_table = mfs_hfl_statement_result_manager.get_metric_results()
    dir_name = "output_mfs_hfl_statement"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(literature_detailed_tables, "mfs_hfl", "statement", dir_name)
    save_overall(literature_overall_table, "mfs_hfl", "statement", dir_name)


def calc_fs_hfl_statement_and_save(fs_hfl_statement_csv_score_items, ground_truth_info, size_counts_info):
    fs_hfl_statement_result_manager = ResultManager(fs_hfl_statement_csv_score_items,
                                                    ground_truth_info,
                                                    size_counts_info,
                                                    True)
    literature_detailed_tables, literature_overall_table = fs_hfl_statement_result_manager.get_metric_results()
    dir_name = "output_fs_hfl_statement"
    file_manager.clean_make_output_dir(dir_name)
    save_detailed(literature_detailed_tables, "fs_hfl", "statement", dir_name)
    save_overall(literature_overall_table, "fs_hfl", "statement", dir_name)


def calc_avg_and_save(avg_csv_score_items, ground_truth_info, size_counts_info):
    granularity_name = avg_csv_score_items[0].get_granularity().name.lower()
    our_metric = granularity_name == FLGranularity.Statement
    avg_result_manager = ResultManager(avg_csv_score_items,
                                       ground_truth_info,
                                       size_counts_info,
                                       our_metric)
    all_detailed_tables, all_overall_table = avg_result_manager.get_metric_results()
    dir_name = f"output_avg_{granularity_name}"
    file_manager.make_if_not_dir(dir_name)
    save_detailed(all_detailed_tables, f"avg", granularity_name, "all", dir_name)
    save_overall(all_overall_table, f"avg", granularity_name, "all", dir_name)
    save_latex_info(all_overall_table, f"avg", granularity_name, "all")


def generate_metrics():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    # file_manager.save_score_items_to_given_directory_path(path_manager.get_statement_csv_score_directory_path(),
    #                                                       fauxpy_statement_csv_score_items)
    calc_fauxpy_statement_and_save(fauxpy_statement_csv_score_items, ground_truth_info, size_counts_info)

    # fauxpy_function_csv_score_items = convert_statement_csv_to_function_csv(path_manager,
    #                                                                         fauxpy_statement_csv_score_items)

    # file_manager.save_score_items_to_given_directory_path(path_manager.get_function_csv_score_directory_path(),
    #                                                       fauxpy_function_csv_score_items)
    # calc_fauxpy_function_and_save(fauxpy_function_csv_score_items, ground_truth_info, size_counts_info)

    # fauxpy_module_csv_score_items = convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items)
    # file_manager.save_score_items_to_given_directory_path(path_manager.get_module_csv_score_directory_path(),
    #                                                       fauxpy_module_csv_score_items)
    # calc_fauxpy_module_and_save(fauxpy_module_csv_score_items, ground_truth_info, size_counts_info)

    # mfs_hfl_statement_csv_score_items = get_mfs_hfl_statement_csv_score_items(fauxpy_statement_csv_score_items,
    #                                                                           fauxpy_function_csv_score_items,
    #                                                                           fauxpy_module_csv_score_items)
    # calc_mfs_hfl_statement_and_save(mfs_hfl_statement_csv_score_items, ground_truth_info, size_counts_info)
    #
    # fs_hfl_statement_csv_score_items = get_fs_hfl_statement_csv_score_items(fauxpy_statement_csv_score_items,
    #                                                                         fauxpy_function_csv_score_items,
    #                                                                         fauxpy_module_csv_score_items)
    # calc_fs_hfl_statement_and_save(fs_hfl_statement_csv_score_items, ground_truth_info, size_counts_info)

    # avg_alfa_statement_csv_score_items = get_avg_csv_score_items(fauxpy_statement_csv_score_items, FLTechnique.AvgAlfa)
    # avg_sbst_statement_csv_score_items = get_avg_csv_score_items(fauxpy_statement_csv_score_items, FLTechnique.AvgSbst)
    # calc_avg_and_save(avg_alfa_statement_csv_score_items + avg_sbst_statement_csv_score_items,
    #                   ground_truth_info, size_counts_info)

    # avg_alfa_function_csv_score_items = get_avg_csv_score_items(fauxpy_function_csv_score_items, FLTechnique.AvgAlfa)
    # avg_sbst_function_csv_score_items = get_avg_csv_score_items(fauxpy_function_csv_score_items, FLTechnique.AvgSbst)
    # calc_avg_and_save(avg_alfa_function_csv_score_items + avg_sbst_function_csv_score_items,
    #                   ground_truth_info, size_counts_info)

    # avg_alfa_module_csv_score_items = get_avg_csv_score_items(fauxpy_module_csv_score_items, FLTechnique.AvgAlfa)
    # avg_sbst_module_csv_score_items = get_avg_csv_score_items(fauxpy_module_csv_score_items, FLTechnique.AvgSbst)
    # calc_avg_and_save(avg_alfa_module_csv_score_items + avg_sbst_module_csv_score_items,
    #                   ground_truth_info, size_counts_info)


def generate_combine_fl_data_input():
    def get_ground_truth_and_size_count(ground_truth: Dict, size_count: Dict,
                                        granularity: FLGranularity) -> Tuple[Dict, Dict]:
        new_ground_truth_dictionary = {}
        for bug_key, module_item_list in ground_truth.items():
            new_module_item_list = []
            for module_item in module_item_list:
                new_module_item = {}
                if granularity == FLGranularity.Statement:
                    new_module_item["FILE_NAME"] = module_item["FILE_NAME"]
                    new_module_item["ITEMS"] = module_item["LINES"] + module_item["EXTENDED_LINES"]
                elif granularity == FLGranularity.Function:
                    new_module_item["FILE_NAME"] = module_item["FILE_NAME"]
                    new_module_item["ITEMS"] = module_item["FUNCTIONS"] + module_item["EXTENDED_FUNCTIONS"]
                elif granularity == FLGranularity.Module:
                    new_module_item["FILE_NAME"] = module_item["FILE_NAME"]
                    new_module_item["ITEMS"] = [module_item["FILE_NAME"]]
                new_module_item_list.append(new_module_item)
            new_ground_truth_dictionary[bug_key] = new_module_item_list

        new_size_count = {}
        for bug_key, value in size_count.items():
            if granularity == FLGranularity.Statement:
                new_size_count[bug_key] = value["LINE_COUNT"]
            elif granularity == FLGranularity.Function:
                new_size_count[bug_key] = value["FUNCTION_COUNT"]
            elif granularity == FLGranularity.Module:
                new_size_count[bug_key] = value["MODULE_COUNT"]

        return new_ground_truth_dictionary, new_size_count

    def generate_data_input_for_granularity(csv_score_items: List[CsvScoreItem], ground_truth, size_counts, dir_name):
        assert any([x.get_granularity() == csv_score_items[0].get_granularity() for x in csv_score_items])
        granularity_name = str(csv_score_items[0].get_granularity().name).lower()

        combine_fl_manager = CombineFlManager(csv_score_items, ground_truth, size_counts)
        release_json_dict_list = combine_fl_manager.get_release_json_dict_list()
        qid_lines_csv_table = combine_fl_manager.get_qid_lines_csv_table()
        fl_tech_str = combine_fl_manager.get_techniques_sorted_as_string()
        proj_string = combine_fl_manager.get_projects_sorted_as_string()
        qid_ground_truth_num_items = combine_fl_manager.get_qid_ground_truth_number_of_items_json_dict()
        output_length = combine_fl_manager.get_output_length()

        for index, release_json_dict_item in enumerate(release_json_dict_list):
            file_manager.save_object_to_json(release_json_dict_item,
                                             Path(dir_name) / f"python_{granularity_name}_release_{index}.json")

        file_manager.save_csv_to_output_dir(qid_lines_csv_table, dir_name,
                                            f"python_{granularity_name}_qid-lines.csv")
        file_manager.save_object_to_json(qid_ground_truth_num_items,
                                         Path(
                                             dir_name) / f"python_{granularity_name}_qid_ground_truth_number_of_items.json")
        file_manager.save_string_to_file(fl_tech_str, Path(dir_name) / "techniques.txt")
        file_manager.save_string_to_file(proj_string, Path(dir_name) / "projects.txt")
        file_manager.save_object_to_json(output_length,
                                         Path(dir_name) / f"python_{granularity_name}_output_length.json")

    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    directory_name = path_manager.get_combine_fl_inputs_dir_name()
    file_manager.make_if_not_dir(directory_name)

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    # Statement level granularity
    # ground_truth_items_statement, size_counts_items_statement = get_ground_truth_and_size_count(ground_truth_info,
    #                                                                                             size_counts_info,
    #                                                                                             FLGranularity.Statement)
    # generate_data_input_for_granularity(fauxpy_statement_csv_score_items,
    #                                     ground_truth_items_statement,
    #                                     size_counts_items_statement,
    #                                     directory_name)

    # Function level granularity
    # fauxpy_function_csv_score_items = convert_statement_csv_to_function_csv(path_manager,
    #                                                                         fauxpy_statement_csv_score_items)
    # ground_truth_items_function, size_counts_items_function = get_ground_truth_and_size_count(ground_truth_info,
    #                                                                                           size_counts_info,
    #                                                                                           FLGranularity.Function)
    # generate_data_input_for_granularity(fauxpy_function_csv_score_items,
    #                                     ground_truth_items_function,
    #                                     size_counts_items_function,
    #                                     directory_name)

    # Module level granularity
    fauxpy_module_csv_score_items = convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items)
    ground_truth_items_module, size_counts_items_module = get_ground_truth_and_size_count(ground_truth_info,
                                                                                          size_counts_info,
                                                                                          FLGranularity.Module)
    generate_data_input_for_granularity(fauxpy_module_csv_score_items,
                                        ground_truth_items_module,
                                        size_counts_items_module,
                                        directory_name)


def generate_latex_data_information():
    path_manager = file_manager.PathManager()
    latex_table_dir_name = path_manager.get_latex_table_dir_name()
    java_paper_info_dir_path = path_manager.get_java_paper_info_dir_path()
    combine_fl_results_dir_name = path_manager.get_combine_fl_results_dir_name()
    combine_fl_input_dir_name = path_manager.get_combine_fl_inputs_dir_name()
    latex_info = LatexInfo(Path(latex_table_dir_name),
                           Path(java_paper_info_dir_path),
                           Path(combine_fl_results_dir_name),
                           Path(combine_fl_input_dir_name))
    latex_info.generate_data_latex_file()


def print_list(list_items):
    for item in list_items:
        print(item)


def get_bug_statistics():
    def print_details(bug_type_list, name_of_type):
        percentage = (len(bug_type_list) / num_all_bugs) * 100
        print(f"{name_of_type}: {len(bug_type_list)}, {round(percentage)}%")

    path_manager = file_manager.PathManager()
    statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    num_all_bugs = len(statement_csv_score_items) / 7
    technique_bugs = [x for x in statement_csv_score_items if x.get_technique() == FLTechnique.Ochiai]

    assert num_all_bugs == len(technique_bugs)

    no_category = [x for x in technique_bugs if
                   not x.get_is_crashing() and
                   not x.get_is_predicate() and
                   not x.get_is_mutable_bug()]

    only_mutable = [x for x in technique_bugs if
                    not x.get_is_crashing() and
                    not x.get_is_predicate() and
                    x.get_is_mutable_bug()]

    only_crashing = [x for x in technique_bugs if
                     x.get_is_crashing() and
                     not x.get_is_predicate() and
                     not x.get_is_mutable_bug()]

    only_predicate = [x for x in technique_bugs if
                      not x.get_is_crashing() and
                      x.get_is_predicate() and
                      not x.get_is_mutable_bug()]

    mutable_predicate = [x for x in technique_bugs if
                         not x.get_is_crashing() and
                         x.get_is_predicate() and
                         x.get_is_mutable_bug()]

    mutable_crashing = [x for x in technique_bugs if
                        x.get_is_crashing() and
                        not x.get_is_predicate() and
                        x.get_is_mutable_bug()]

    crashing_predicate = [x for x in technique_bugs if
                          x.get_is_crashing() and
                          x.get_is_predicate() and
                          not x.get_is_mutable_bug()]

    mutable_crashing_predicate = [x for x in technique_bugs if
                                  x.get_is_crashing() and
                                  x.get_is_predicate() and
                                  x.get_is_mutable_bug()]

    any_crashing = [x for x in technique_bugs if x.get_is_crashing()]
    an_predicate = [x for x in technique_bugs if x.get_is_predicate()]
    any_mutable = [x for x in technique_bugs if x.get_is_mutable_bug()]

    print("no_category", len(no_category))
    print("only_mutable", len(only_mutable))
    print("only_crashing", len(only_crashing))
    print("only_predicate", len(only_predicate))
    print("mutable_predicate", len(mutable_predicate))
    print("mutable_crashing", len(mutable_crashing))
    print("crashing_predicate", len(crashing_predicate))
    print("mutable_crashing_predicate", len(mutable_crashing_predicate))

    print("any_crashing", len(any_crashing))
    print("an_predicate", len(an_predicate))
    print("any_mutable", len(any_mutable))

    print_list(only_predicate)


def get_project_statistics():
    path_manager = file_manager.PathManager()
    statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    num_all_bugs = len(statement_csv_score_items) / 7
    technique_bugs = [x for x in statement_csv_score_items if x.get_technique() == FLTechnique.Ochiai]

    assert num_all_bugs == len(technique_bugs)

    cli_num = [x for x in technique_bugs if x.get_project_type() == ProjectType.CLI]
    dev_num = [x for x in technique_bugs if x.get_project_type() == ProjectType.Dev]
    ds_num = [x for x in technique_bugs if x.get_project_type() == ProjectType.DS]
    web_num = [x for x in technique_bugs if x.get_project_type() == ProjectType.Web]

    httpie = [x for x in technique_bugs if x.get_project_name() == "httpie"]
    thefuck = [x for x in technique_bugs if x.get_project_name() == "thefuck"]
    tqdm = [x for x in technique_bugs if x.get_project_name() == "tqdm"]
    youtube_dl = [x for x in technique_bugs if x.get_project_name() == "youtube-dl"]
    black = [x for x in technique_bugs if x.get_project_name() == "black"]
    cookiecutter = [x for x in technique_bugs if x.get_project_name() == "cookiecutter"]
    luigi = [x for x in technique_bugs if x.get_project_name() == "luigi"]
    keras = [x for x in technique_bugs if x.get_project_name() == "keras"]
    pandas = [x for x in technique_bugs if x.get_project_name() == "pandas"]
    spacy = [x for x in technique_bugs if x.get_project_name() == "spacy"]
    fastapi = [x for x in technique_bugs if x.get_project_name() == "fastapi"]
    sanic = [x for x in technique_bugs if x.get_project_name() == "sanic"]
    tornado = [x for x in technique_bugs if x.get_project_name() == "tornado"]

    print("cli_num", len(cli_num))
    print("dev_num", len(dev_num))
    print("ds_num", len(ds_num))
    print("web_num", len(web_num))

    print("httpie", len(httpie))
    print("thefuck", len(thefuck))
    print("tqdm", len(tqdm))
    print("youtube_dl", len(youtube_dl))
    print("black", len(black))
    print("cookiecutter", len(cookiecutter))
    print("luigi", len(luigi))
    print("keras", len(keras))
    print("pandas", len(pandas))
    print("spacy", len(spacy))
    print("fastapi", len(fastapi))
    print("sanic", len(sanic))
    print("tornado", len(tornado))


def get_ground_truth_statistics():
    def compute_num_ground_truth(project_name, tech_bug_list) -> int:
        ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
        bug_key_list = [x.get_bug_key() for x in tech_bug_list if x.get_bug_key().startswith(project_name)]

        number_ground_items = 0
        for bug_key, bug_value in ground_truth_info.items():
            if bug_key in bug_key_list:
                for file_item in bug_value:
                    len_lines = len(file_item["LINES"])
                    len_extended_lines = len(file_item["EXTENDED_LINES"])
                    number_ground_items += len_lines + len_extended_lines

        return number_ground_items

    path_manager = file_manager.PathManager()
    statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    num_all_bugs = len(statement_csv_score_items) / 7
    technique_bugs = [x for x in statement_csv_score_items if x.get_technique() == FLTechnique.Ochiai]
    assert num_all_bugs == len(technique_bugs)

    httpie = compute_num_ground_truth("httpie", technique_bugs)
    thefuck = compute_num_ground_truth("thefuck", technique_bugs)
    tqdm = compute_num_ground_truth("tqdm", technique_bugs)
    youtube_dl = compute_num_ground_truth("youtube-dl", technique_bugs)
    black = compute_num_ground_truth("black", technique_bugs)
    cookiecutter = compute_num_ground_truth("cookiecutter", technique_bugs)
    luigi = compute_num_ground_truth("luigi", technique_bugs)
    keras = compute_num_ground_truth("keras", technique_bugs)
    pandas = compute_num_ground_truth("pandas", technique_bugs)
    spacy = compute_num_ground_truth("spacy", technique_bugs)
    fastapi = compute_num_ground_truth("fastapi", technique_bugs)
    sanic = compute_num_ground_truth("sanic", technique_bugs)
    tornado = compute_num_ground_truth("tornado", technique_bugs)

    print("httpie", httpie)
    print("thefuck", thefuck)
    print("tqdm", tqdm)
    print("youtube_dl", youtube_dl)
    print("black", black)
    print("cookiecutter", cookiecutter)
    print("luigi", luigi)
    print("keras", keras)
    print("pandas", pandas)
    print("spacy", spacy)
    print("fastapi", fastapi)
    print("sanic", sanic)
    print("tornado", tornado)

    all_len = [httpie, thefuck,
               tqdm, youtube_dl,
               black, cookiecutter,
               luigi, keras,
               pandas, spacy,
               fastapi, sanic,
               tornado]

    print("all_len", sum(all_len))


def get_within_text_statistics():
    path_manager = file_manager.PathManager()
    statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    metallaxis_csv_items = [x for x in statement_csv_score_items
                            if x.get_technique() == FLTechnique.Metallaxis]

    metallaxis_csv_items.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))

    number_of_mutants_list = [x.get_number_of_mutants() for x in metallaxis_csv_items]

    average_number_of_mutants = mathematics.average(number_of_mutants_list)
    print("average_number_of_mutants", average_number_of_mutants)

    max_number_of_mutants = max(number_of_mutants_list)
    print("max_number_of_mutants", max_number_of_mutants)

    bug_key_of_maximum_number_of_mutants = [x.get_bug_key() for x in metallaxis_csv_items
                                            if x.get_number_of_mutants() == max_number_of_mutants]
    print("bug_key_of_maximum_number_of_mutants", bug_key_of_maximum_number_of_mutants)

    non_empty_critical_predicate_csv_items = get_non_empty_critical_predicate_csv_items(
        statement_csv_score_items)

    crashing_critical_predicate = [x for x in non_empty_critical_predicate_csv_items
                                   if x.get_technique() == FLTechnique.Metallaxis and
                                   x.get_is_crashing()]
    print("number of crashing_critical_predicate", len(crashing_critical_predicate))


def get_tool_demo_paper_table_info():
    def compute_metrics(csv_items, bug_type):
        fauxpy_statement_result_manager = ResultManager(csv_items,
                                                        ground_truth_info,
                                                        size_counts_info)
        _, all_overall_table = fauxpy_statement_result_manager.get_metric_results()
        save_overall(all_overall_table, "fauxpy", "statement", bug_type, dir_name)

        technique_overall_file_name = f"fauxpy_statement_{bug_type}_overall.json"
        file_path = Path(dir_name) / technique_overall_file_name
        file_manager.save_object_to_json(all_overall_table, file_path)

    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())
    statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    httpie = [x for x in statement_csv_score_items if x.get_project_name() == "httpie"]
    thefuck = [x for x in statement_csv_score_items if x.get_project_name() == "thefuck"]
    tqdm = [x for x in statement_csv_score_items if x.get_project_name() == "tqdm"]
    youtube_dl = [x for x in statement_csv_score_items if x.get_project_name() == "youtube-dl"]
    black = [x for x in statement_csv_score_items if x.get_project_name() == "black"]
    cookiecutter = [x for x in statement_csv_score_items if x.get_project_name() == "cookiecutter"]
    luigi = [x for x in statement_csv_score_items if x.get_project_name() == "luigi"]
    keras = [x for x in statement_csv_score_items if x.get_project_name() == "keras"]
    pandas = [x for x in statement_csv_score_items if x.get_project_name() == "pandas"]
    spacy = [x for x in statement_csv_score_items if x.get_project_name() == "spacy"]
    fastapi = [x for x in statement_csv_score_items if x.get_project_name() == "fastapi"]
    sanic = [x for x in statement_csv_score_items if x.get_project_name() == "sanic"]
    tornado = [x for x in statement_csv_score_items if x.get_project_name() == "tornado"]

    all_csv_subject_list = [(httpie, "httpie"), (thefuck, "thefuck"),
                            (tqdm, "tqdm"), (youtube_dl, "youtube_dl"),
                            (black, "black"), (cookiecutter, "cookiecutter"),
                            (luigi, "luigi"), (keras, "keras"),
                            (pandas, "pandas"), (spacy, "spacy"),
                            (fastapi, "fastapi"), (sanic, "sanic"),
                            (tornado, "tornado")]

    dir_name = "tool_demo_paper"
    project_count_file_path = Path(dir_name) / "project_count.json"
    file_manager.make_if_not_dir(dir_name)

    project_count_dict = {}

    for subject_csv, subject_name in all_csv_subject_list:
        project_count_dict[subject_name] = int(len(subject_csv) / 7)
        compute_metrics(subject_csv, subject_name)

    file_manager.save_object_to_json(project_count_dict, project_count_file_path)

    latex_info_object = latex_inf_generator_tool_demo.LatexInfo(Path(dir_name),
                                                                project_count_file_path)
    latex_info_object.generate()


if __name__ == '__main__':
    # generate_metrics()
    # generate_combine_fl_data_input()
    # generate_latex_data_information()
    # get_bug_statistics()
    # get_project_statistics()
    # get_ground_truth_statistics()
    # get_within_text_statistics()
    get_tool_demo_paper_table_info()
