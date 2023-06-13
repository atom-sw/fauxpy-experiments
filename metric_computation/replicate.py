import sys

import file_manager
from compute_all import (get_fauxpy_statement_csv_score_items,
                         calc_fauxpy_statement_and_save,
                         convert_statement_csv_to_function_csv,
                         calc_fauxpy_function_and_save, convert_statement_csv_to_module_csv,
                         calc_fauxpy_module_and_save, get_avg_csv_score_items, calc_avg_and_save,
                         generate_combine_fl_data_input, generate_latex_data_information)
from csv_score_load_manager import FLTechnique


def fauxpy_statement_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    file_manager.save_score_items_to_given_directory_path(path_manager.get_statement_csv_score_directory_path(),
                                                          fauxpy_statement_csv_score_items)
    calc_fauxpy_statement_and_save(fauxpy_statement_csv_score_items,
                                   ground_truth_info, size_counts_info)


def fauxpy_function_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    fauxpy_function_csv_score_items = convert_statement_csv_to_function_csv(path_manager,
                                                                            fauxpy_statement_csv_score_items)

    file_manager.save_score_items_to_given_directory_path(path_manager.get_function_csv_score_directory_path(),
                                                          fauxpy_function_csv_score_items)
    calc_fauxpy_function_and_save(fauxpy_function_csv_score_items, ground_truth_info, size_counts_info)


def fauxpy_module_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    fauxpy_module_csv_score_items = convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items)
    file_manager.save_score_items_to_given_directory_path(path_manager.get_module_csv_score_directory_path(),
                                                          fauxpy_module_csv_score_items)
    calc_fauxpy_module_and_save(fauxpy_module_csv_score_items, ground_truth_info, size_counts_info)


def avg_statement_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)

    avg_alfa_statement_csv_score_items = get_avg_csv_score_items(fauxpy_statement_csv_score_items,
                                                                 FLTechnique.AvgAlfa)
    avg_sbst_statement_csv_score_items = get_avg_csv_score_items(fauxpy_statement_csv_score_items,
                                                                 FLTechnique.AvgSbst)
    calc_avg_and_save(avg_alfa_statement_csv_score_items + avg_sbst_statement_csv_score_items,
                      ground_truth_info, size_counts_info)


def avg_function_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)
    fauxpy_function_csv_score_items = convert_statement_csv_to_function_csv(path_manager,
                                                                            fauxpy_statement_csv_score_items)

    avg_alfa_function_csv_score_items = get_avg_csv_score_items(fauxpy_function_csv_score_items,
                                                                FLTechnique.AvgAlfa)
    avg_sbst_function_csv_score_items = get_avg_csv_score_items(fauxpy_function_csv_score_items,
                                                                FLTechnique.AvgSbst)
    calc_avg_and_save(avg_alfa_function_csv_score_items + avg_sbst_function_csv_score_items,
                      ground_truth_info, size_counts_info)


def avg_module_results():
    path_manager = file_manager.PathManager()
    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    size_counts_info = file_manager.load_json_to_object(path_manager.get_size_counts_file_name())

    fauxpy_statement_csv_score_items = get_fauxpy_statement_csv_score_items(path_manager)
    fauxpy_module_csv_score_items = convert_statement_csv_to_module_csv(fauxpy_statement_csv_score_items)

    avg_alfa_module_csv_score_items = get_avg_csv_score_items(fauxpy_module_csv_score_items,
                                                              FLTechnique.AvgAlfa)
    avg_sbst_module_csv_score_items = get_avg_csv_score_items(fauxpy_module_csv_score_items,
                                                              FLTechnique.AvgSbst)
    calc_avg_and_save(avg_alfa_module_csv_score_items + avg_sbst_module_csv_score_items,
                      ground_truth_info, size_counts_info)


def generate_combine_fl_inputs():
    generate_combine_fl_data_input()


def generate_latex_data_tex_file():
    generate_latex_data_information()


def main():
    assert len(sys.argv) == 2
    if int(sys.argv[1]) == 1:
        fauxpy_statement_results()
    elif int(sys.argv[1]) == 2:
        fauxpy_function_results()
    elif int(sys.argv[1]) == 3:
        fauxpy_module_results()
    elif int(sys.argv[1]) == 4:
        avg_statement_results()
    elif int(sys.argv[1]) == 5:
        avg_function_results()
    elif int(sys.argv[1]) == 6:
        avg_module_results()
    elif int(sys.argv[1]) == 7:
        generate_combine_fl_inputs()
    elif int(sys.argv[1]) == 8:
        generate_latex_data_tex_file()


if __name__ == '__main__':
    main()
