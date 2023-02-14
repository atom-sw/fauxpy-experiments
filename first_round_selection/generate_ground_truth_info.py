import re
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Optional

import common

CORRECT = {}
PATCH_INFO_FILE_NAME: str = "ground_truth_info.json"


class ConsumeMode(Enum):
    Normal = 0
    Remove = 1
    Edit = 2
    Add = 3


def get_patch_parts(patch) -> List[List[str]]:
    patch_parts = []
    # patch_lines = patch.split("\n")
    patch_lines = patch.splitlines()
    part_lines = []
    for patch_line in patch_lines:
        meta_line_list = re.findall(r"@@.*@@", patch_line)
        if len(meta_line_list) > 0:
            if len(part_lines) > 0:
                patch_parts.append(part_lines)
            part_lines = []
        part_lines.append(patch_line)
    patch_parts.append(part_lines)

    return patch_parts


def get_patch_part_meta_info_buggy_lines(meta_info_line: str):
    meta_info_list_buggy_start = re.findall(r"@@ -(\d+).*@@", meta_info_line)
    meta_info_list_buggy_number_lines = re.findall(r"@@ -\d+,(\d+).*@@", meta_info_line)
    assert len(meta_info_list_buggy_start) == 1
    assert len(meta_info_list_buggy_number_lines) == 1
    starting_buggy_line = meta_info_list_buggy_start[0]
    number_buggy_line = meta_info_list_buggy_number_lines[0]
    return int(starting_buggy_line), int(number_buggy_line)


def is_code_line(line: str):
    line_strip = line.strip()
    return (line_strip != "" and
            not line_strip.startswith("#") and
            not line_strip.startswith("'''") and
            not line_strip.startswith('"""'))


def diff_index_to_buggy_index(lines: List[str],
                              diff_index: int):
    offset = 0
    for index in range(0, diff_index):
        if lines[index].startswith("+"):
            offset += 1

    return diff_index - offset


def consume(lines: List[str],
            patch_part_starting_line: int,
            buggy_content_lines: Optional[List[str]]) -> Tuple[List[int], List[int]]:
    """
    This function implements a state machine that consumes diffs
    to figure out which lines need to be included in
    the ground truth (i.e., code_lines). It looks for
    three cases:

    1. one or more minus (-) signs, which means remove.
    they should all be included in the ground truth.

    2. One or more plus (+) signs, proceeding one or more minus
    signs which means edit. In this case, only the removed lines
    are included in the ground truth.

    3. One or more plus signs with no minus signs
    before them, which means add.
    In this case, the code line (not empty or comment lines) coming
    right after the plus signs is added to the ground truth.
    We also add the code line before the plus signs to the
    extended version of the ground truth (i.e., code_extended_lines).
    """

    code_lines = []
    code_extended_lines = []
    consume_mode = ConsumeMode.Normal

    start_add_index = None
    end_add_index = None

    none_code_line_removed_in_edit_counter = 0
    code_line_added_in_edit_counter = 0

    for index, line in enumerate(lines):
        if line.startswith("-"):
            assert consume_mode == ConsumeMode.Normal or consume_mode == ConsumeMode.Remove

            consume_mode = ConsumeMode.Remove
            rel_buggy_index = diff_index_to_buggy_index(lines, index)
            abs_buggy_index = rel_buggy_index + patch_part_starting_line
            if abs_buggy_index not in code_lines:
                code_lines.append(abs_buggy_index)
                if not is_code_line(line[1:]):
                    none_code_line_removed_in_edit_counter += 1
        elif line.startswith("+"):
            if consume_mode == ConsumeMode.Normal:
                consume_mode = ConsumeMode.Add
            elif consume_mode == ConsumeMode.Remove:
                consume_mode = ConsumeMode.Edit
                # Ignore the added lines.

            if consume_mode == ConsumeMode.Add:
                if start_add_index is None:
                    start_add_index = index
                end_add_index = index
            elif consume_mode == ConsumeMode.Edit:
                if is_code_line(line[1:]):
                    code_line_added_in_edit_counter += 1
        else:
            if consume_mode == ConsumeMode.Edit:
                if (none_code_line_removed_in_edit_counter == len(code_lines) and
                        code_line_added_in_edit_counter != 0):
                    print("Manual check! Edit none code!")

            none_code_line_removed_in_edit_counter = 0
            code_line_added_in_edit_counter = 0

            if consume_mode == ConsumeMode.Add:
                for ind in range(end_add_index + 1, len(lines)):
                    if is_code_line(lines[ind]):
                        rel_buggy_index = diff_index_to_buggy_index(lines, ind)
                        abs_buggy_index = rel_buggy_index + patch_part_starting_line
                        if abs_buggy_index not in code_lines:
                            code_lines.append(abs_buggy_index)
                        break

                for ind in range(start_add_index - 1, -1, -1):
                    if is_code_line(lines[ind]):
                        rel_buggy_index = diff_index_to_buggy_index(lines, ind)
                        abs_buggy_index = rel_buggy_index + patch_part_starting_line
                        if abs_buggy_index not in code_extended_lines and abs_buggy_index not in code_lines:
                            code_extended_lines.append(abs_buggy_index)
                        break

            consume_mode = ConsumeMode.Normal
            start_add_index = None
            end_add_index = None

    return code_lines, code_extended_lines


def get_file_ground_truth(patch: str, buggy_content: str) -> Tuple[List[int], List[int]]:
    code_lines = []
    code_extended_lines = []

    buggy_content_lines = buggy_content.splitlines() if buggy_content is not None else None
    patch_parts = get_patch_parts(patch)
    for patch_part in patch_parts:
        meta_info_line = patch_part[0]
        starting_buggy_line, number_buggy_line = get_patch_part_meta_info_buggy_lines(meta_info_line)
        lines = patch_part[1:]
        current_code_lines, current_code_extended_lines = consume(lines, starting_buggy_line, buggy_content_lines)
        # code_lines += [x + starting_buggy_line for x in relative_code_lines]
        # code_extended_lines += [x + starting_buggy_line for x in relative_code_extended_lines]
        code_lines += current_code_lines
        code_extended_lines += current_code_extended_lines
    return code_lines, code_extended_lines


def get_bug_ground_truth(benchmark_name: str,
                         bug_number: int):
    python_none_test_files = common.get_diff_commit(benchmark_name, bug_number)

    but_ground_truth = []

    # python_none_test_files = list(filter(lambda x:
    #                                      x.filename.endswith(".py") and
    #                                      "test/" not in x.filename and
    #                                      "tests/" not in x.filename,
    #                                      diff_commit.files))

    for file in python_none_test_files:
        filename = file.filename
        patch = file.patch
        buggy_content = file.buggy_content
        lines, extended_lines = get_file_ground_truth(patch, buggy_content)
        but_ground_truth.append(
            {
                "FILE_NAME": filename,
                "LINES": lines,
                "EXTENDED_LINES": extended_lines
            }
        )
    return but_ground_truth


def calculate_all_line_nums(bug_patch_info):
    lines_num = 0
    for item in bug_patch_info:
        lines_num += len(item["LINES"])

    return lines_num


def main():
    global CORRECT

    CORRECT = common.load_correct_test_bugs()

    patch_info_dict = {}

    for benchmark_name, benchmark_items in CORRECT.items():
        for bug_number in benchmark_items["ACCEPTED"]:

            # if benchmark_name != "pandas":
            #     continue

            print(benchmark_name, bug_number)
            bug_patch_info = get_bug_ground_truth(benchmark_name, bug_number)
            all_line_nums = calculate_all_line_nums(bug_patch_info)
            if all_line_nums <= 0:
                print("Manual check! Empty lines in: ", benchmark_name, bug_number)
            patch_info_dict[f"{benchmark_name}:{bug_number}"] = bug_patch_info

    common.save_object_to_json(patch_info_dict, Path(PATCH_INFO_FILE_NAME))


if __name__ == '__main__':
    main()
