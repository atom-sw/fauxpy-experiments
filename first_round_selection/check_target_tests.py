import re
from pathlib import Path
from typing import Tuple

import common

INPUTS = {}
WORKSPACE = {}


def are_equal_list_items(list_items):
    for item_a in list_items:
        for item_b in list_items:
            if item_a != item_b:
                return False

    return True


def get_pytest_match(content, pattern):
    """
    Probably, benchmark specific.
    """

    regex = re.compile(pattern)
    matches = regex.findall(content)
    assert len(matches) <= 1 or are_equal_list_items(matches)
    return 0 if len(matches) == 0 else int(matches[-1])


# def get_unittest_match(content, pattern):
#     """
#     Probably, benchmark specific.
#     """
#
#     regex = re.compile(pattern)
#     matches = regex.findall(content)
#     assert len(matches) <= 1
#     return 0 if len(matches) == 0 else int(matches[-1])


# def get_test_info(version_path: Path) -> Tuple[int, int, int]:
#     """
#     Probably, benchmark specific.
#     """
#     test_output_stdout = version_path / common.TEST_OUTPUT_FILE_STDOUT
#     test_output_stderr = version_path / common.TEST_OUTPUT_FILE_STDERR
#
#     stderr_content = common.read_file_content(test_output_stderr)
#     assert stderr_content == ""
#
#     stdout_content = common.read_file_content(test_output_stdout)
#
#     failed = get_pytest_match(stdout_content, fr"(\d) failed")
#     passed = get_pytest_match(stdout_content, fr"(\d) passed")
#     error = get_pytest_match(stdout_content, fr"(\d) error")
#
#     # if INPUTS["BENCHMARK_NAME"] == "keras":
#     #     failed = get_pytest_match(stdout_content, fr"(\d) failed")
#     #     passed = get_pytest_match(stdout_content, fr"(\d) passed")
#     #     error = get_pytest_match(stdout_content, fr"(\d) error")
#     # elif INPUTS["BENCHMARK_NAME"] == "youtube-dl":
#     #     failed = get_unittest_match(stdout_content, fr"FAILED (failures=(\d))")
#     #     passed = get_unittest_match(stdout_content, fr"Ran (\d) test in *\nOK")
#     #     error = get_unittest_match(stdout_content, fr"FAILED (errors=(\d))")
#     #     pass
#     # else:
#     #     raise Exception("Benchmark not supported.")
#
#     return failed, passed, error


def get_pytest_info(content):
    passed = get_pytest_match(content, fr"(\d) passed")
    failed = get_pytest_match(content, fr"(\d) failed")
    error = get_pytest_match(content, fr"(\d) error")

    return passed, failed, error


def get_unittest_info(content):
    raise Exception("Not implemented.")


def get_target_tests_info(version_path: Path):
    test_output_stdout = version_path / common.TEST_OUTPUT_FILE_STDOUT
    test_output_stderr = version_path / common.TEST_OUTPUT_FILE_STDERR

    stderr_content = common.read_file_content(test_output_stderr)
    assert stderr_content == ""

    stdout_content = common.read_file_content(test_output_stdout)

    if ("pytest" in stdout_content and
            "test session starts" in stdout_content):
        return get_pytest_info(stdout_content)
    elif ("unittest" in stdout_content and
          "RUN EVERY COMMAND" in stdout_content and
          "Ran" in stdout_content):
        return get_unittest_info(stdout_content)
    else:
        raise Exception("Problem here!")


def is_included(bug_number: int):
    workspace_path = WORKSPACE["WORKSPACE_PATH"]
    benchmark_name = INPUTS['BENCHMARK_NAME']
    buggy_path = common.get_buggy_project_path(workspace_path,
                                               benchmark_name,
                                               bug_number)
    fixed_path = common.get_fixed_project_path(workspace_path,
                                               benchmark_name,
                                               bug_number)
    b_passed, b_failed, b_error = get_target_tests_info(buggy_path)
    f_passed, f_failed, f_error = get_target_tests_info(fixed_path)

    return (b_failed > 0 and
            f_passed > 0 and
            f_error == 0 and
            b_failed + b_passed ==
            f_failed + f_passed)


def main():
    global INPUTS
    global WORKSPACE

    project_info_file_path = common.get_project_info_file_path()

    INPUTS = common.load_json_to_dictionary(project_info_file_path)
    WORKSPACE = common.load_json_to_dictionary(common.WORKSPACE_FILE_NAME)

    accepted_bugs = []
    rejected_bugs = []

    benchmark_name = INPUTS['BENCHMARK_NAME']

    for current_bug_number in range(INPUTS["BUG_NUMBER_START"], INPUTS["BUG_NUMBER_END"] + 1):
        print(f"{benchmark_name}{current_bug_number}")
        if is_included(current_bug_number):
            print("Accepted")
            accepted_bugs.append(current_bug_number)
        else:
            print("Rejected")
            rejected_bugs.append(current_bug_number)

    file_path_accepted = common.get_output_dir() / f"{INPUTS['BENCHMARK_NAME']}_accepted_bugs.json"
    file_path_rejected = common.get_output_dir() / f"{INPUTS['BENCHMARK_NAME']}_rejected_bugs.json"

    common.save_object_to_json(accepted_bugs, file_path_accepted)
    common.save_object_to_json(rejected_bugs, file_path_rejected)


if __name__ == '__main__':
    main()
