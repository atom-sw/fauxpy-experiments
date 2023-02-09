import re
from pathlib import Path
from typing import Tuple, List

import common

CORRECT = {}
PATCH_INFO_FILE_NAME: str = "ground_truth_info.json"


def get_patch_parts(patch) -> List[List[str]]:
    patch_parts = []
    patch_lines = patch.split("\n")
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


def get_file_ground_truth(patch: str) -> Tuple[List[int], List[int]]:
    patch_parts = get_patch_parts(patch)
    for patch_part in patch_parts:
        meta_info_line = patch_part[0]
        lines = patch_part[1:]
        print(lines)
    return [], []


def get_bug_ground_truth(benchmark_name: str,
                         bug_number: int):
    diff_commit = common.get_diff_commit(benchmark_name, bug_number)

    but_ground_truth = []

    for file in diff_commit.files:
        filename = file.filename
        patch = file.patch
        lines, extended_lines = get_file_ground_truth(patch)
        but_ground_truth.append(
            {
                "FILE_NAME": filename,
                "LINES": lines,
                "EXTENDED_LINES": extended_lines
            }
        )
    return but_ground_truth


def main():
    global CORRECT

    CORRECT = common.load_correct_test_bugs()

    patch_info_dict = {}

    for benchmark_name, benchmark_items in CORRECT.items():
        if benchmark_name != "sanic":
            continue

        for bug_number in benchmark_items["ACCEPTED"]:
            print(benchmark_name, bug_number)
            bug_patch_info = get_bug_ground_truth(benchmark_name, bug_number)
            print(bug_patch_info)
            patch_info_dict[f"{benchmark_name}:{bug_number}"] = bug_patch_info

    common.save_object_to_json(patch_info_dict, Path(PATCH_INFO_FILE_NAME))


if __name__ == '__main__':
    main()
    pass
