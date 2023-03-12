from pathlib import Path
from typing import List, Tuple

import common
import ast_function_manager

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


def get_line_function_counts(benchmark_name: str,
                             bug_number: int,
                             target_dir: str,
                             exclude: List[str]) -> Tuple[int, int]:
    """
    1. Counts the number of non-empty and non-comment lines.
    2. Only counts line numbers and number of functions in the target directory.
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
        current_function_num = ast_function_manager.count_function_num(item)
        counter_line += current_loc
        counter_function += current_function_num

    return counter_line, counter_function


def load_info_files():
    info = {}
    json_files = list(Path(common.SUBJECT_INFO_DIRECTORY_NAME).rglob("*.json"))
    json_files.sort()
    for item in json_files:
        benchmark_info = common.load_json_to_dictionary(str(item.absolute().resolve()))
        info[benchmark_info["BENCHMARK_NAME"]] = benchmark_info

    return info


def main():
    # cache_manager = common.CacheManager(CACHE_DIR_NAME)
    correct_test_bugs_dict = common.load_correct_test_bugs()
    info_files_dict = load_info_files()

    line_numbers_dict = {}

    for benchmark_name, benchmark_items in correct_test_bugs_dict.items():
        for bug_number in benchmark_items["ACCEPTED"]:
            print(benchmark_name, bug_number)
            target_dir = info_files_dict[benchmark_name]["TARGET_DIR"]
            exclude = info_files_dict[benchmark_name]["EXCLUDE"]

            # cache_file_name_current = f"{benchmark_name}_{bug_number}"
            # cache_obj = cache_manager.load(cache_file_name_current)
            # if cache_obj is None:
            #     line_count, function_count = get_line_function_counts(benchmark_name, bug_number, target_dir, exclude)
            #     cache_manager.save((line_count, function_count), cache_file_name_current)
            # else:
            #     line_count, function_count = cache_obj

            line_count, function_count = get_line_function_counts(benchmark_name, bug_number, target_dir, exclude)
            print(line_count, function_count)

            current_key = f"{benchmark_name}:{bug_number}"
            line_numbers_dict[current_key] = {"LINE_COUNT": line_count,
                                              "FUNCTION_COUNT": function_count}

    common.save_object_to_json(line_numbers_dict, Path(LINE_COUNT_FILE_NAME))


if __name__ == '__main__':
    main()
