from pathlib import Path
from typing import Dict

import common

CORRECT = {}
PATCH_INFO_FILE_NAME: str = "patch_info.json"


def get_patch_bug_info(benchmark_name: str,
                       bug_number: int) -> Dict:
    current_changed_files = common.get_changed_modules(benchmark_name, bug_number)
    current_patch = common.get_patch(benchmark_name, bug_number)
    patches = list(map(lambda x: x.patch, current_patch.files))
    return {
        "FILE_NAME": current_changed_files,
        "PATCH": patches
    }


def main():
    global CORRECT

    CORRECT = common.load_correct_test_bugs()

    patch_info_dict = {}

    for benchmark_name, benchmark_items in CORRECT.items():
        if benchmark_name == "pandas":
            continue

        for bug_number in benchmark_items["ACCEPTED"]:
            print(benchmark_name, bug_number)
            bug_patch_info = get_patch_bug_info(benchmark_name, bug_number)
            print(bug_patch_info)
            patch_info_dict[f"{benchmark_name}:{bug_number}"] = bug_patch_info

    common.save_object_to_json(patch_info_dict, Path(PATCH_INFO_FILE_NAME))


if __name__ == '__main__':
    main()
    pass
