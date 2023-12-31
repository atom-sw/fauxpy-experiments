from pathlib import Path
from typing import List, Tuple

import common
import ast_function_counter

LINE_COUNT_FILE_NAME = "size_counts.json"
CACHE_DIR_NAME = "cache_size_count"


def get_non_excluded_python_file_paths(target_dir_path: Path,
                                       excluded_dir_path_list: List[Path]) -> List[Path]:
    non_excluded_python_file_paths = []
    all_python_in_target_dir = list(target_dir_path.rglob("*.py"))

    excluded_python_file_paths = []
    for item in excluded_dir_path_list:
        current_excluded_python_paths = list(item.rglob("*.py"))
        excluded_python_file_paths += current_excluded_python_paths

    for item in all_python_in_target_dir:
        if item not in excluded_python_file_paths:
            non_excluded_python_file_paths.append(item)

    return non_excluded_python_file_paths


def is_comment_line(line_item):
    return line_item.strip().startswith("#")


def is_empty_line(line_item):
    return line_item.strip() == ""


def get_module_loc(module_path: Path) -> int:
    assert module_path.name.endswith(".py")

    module_content = common.read_file_content(module_path)
    module_lines = module_content.splitlines()

    line_counter = 0
    for line_item in module_lines:
        if not is_comment_line(line_item) and not is_empty_line(line_item):
            line_counter += 1

    return line_counter


def get_line_function_module_counts(benchmark_name: str,
                                    bug_number: int,
                                    target_dir: str,
                                    exclude: List[str]) -> Tuple[int, int, int]:
    """
    1. Counts the number of non-empty and non-comment lines.
    2. Only counts line numbers, number of functions, and
        number of modules in the target directory.
    3. Does not count excluded directories.
    """

    buggy_project_directory_path = common.get_buggy_project_path(benchmark_name, bug_number)
    target_dir_path = buggy_project_directory_path / target_dir
    excluded_dir_path_list = [buggy_project_directory_path / x for x in exclude]

    non_excluded_python_file_paths = get_non_excluded_python_file_paths(target_dir_path, excluded_dir_path_list)

    counter_line = 0
    counter_function = 0
    for item in non_excluded_python_file_paths:
        current_loc = get_module_loc(item)
        current_function_num = ast_function_counter.count_function_num(item)
        counter_line += current_loc
        counter_function += current_function_num

    counter_module = len(non_excluded_python_file_paths)

    return counter_line, counter_function, counter_module


def load_info_files():
    info = {}
    json_files = list(Path(common.SUBJECT_INFO_DIRECTORY_NAME).rglob("*.json"))
    json_files.sort()
    for item in json_files:
        benchmark_info = common.load_json_to_dictionary(str(item.absolute().resolve()))
        info[benchmark_info["BENCHMARK_NAME"]] = benchmark_info

    return info


def load_info_files_2():
    info = {}
    json_files = list(Path(common.SUBJECT_INFO_DIRECTORY_NAME_2).rglob("*.json"))
    json_files.sort()
    for item in json_files:
        benchmark_info = common.load_json_to_dictionary(str(item.absolute().resolve()))
        info[benchmark_info["BENCHMARK_NAME"]] = benchmark_info

    return info


def main():
    correct_test_bugs_dict = common.load_correct_test_bugs()
    correct_test_bugs_dict_2 = common.load_correct_test_bugs_2()
    info_files_dict = load_info_files()
    info_files_dict_2 = load_info_files_2()

    line_numbers_dict = {}

    for benchmark_name, benchmark_items in correct_test_bugs_dict.items():
        for bug_number in benchmark_items["ACCEPTED"]:
            print(benchmark_name, bug_number)
            target_dir = info_files_dict[benchmark_name]["TARGET_DIR"]
            exclude = info_files_dict[benchmark_name]["EXCLUDE"]

            line_count, function_count, module_count = get_line_function_module_counts(benchmark_name, bug_number,
                                                                                       target_dir, exclude)
            print(line_count, function_count, module_count)

            current_key = f"{benchmark_name}:{bug_number}"
            line_numbers_dict[current_key] = {"LINE_COUNT": line_count,
                                              "FUNCTION_COUNT": function_count,
                                              "MODULE_COUNT": module_count}

    for benchmark_name, benchmark_items in correct_test_bugs_dict_2.items():
        for bug_number in benchmark_items["ACCEPTED"]:
            print(benchmark_name, bug_number)
            target_dir = info_files_dict_2[benchmark_name]["TARGET_DIR"]
            exclude = info_files_dict_2[benchmark_name]["EXCLUDE"]

            line_count, function_count, module_count = get_line_function_module_counts(benchmark_name, bug_number,
                                                                                       target_dir, exclude)
            print(line_count, function_count, module_count)

            current_key = f"{benchmark_name}:{bug_number}"
            line_numbers_dict[current_key] = {"LINE_COUNT": line_count,
                                              "FUNCTION_COUNT": function_count,
                                              "MODULE_COUNT": module_count}

    common.save_object_to_json(line_numbers_dict, Path(LINE_COUNT_FILE_NAME))


if __name__ == '__main__':
    main()
