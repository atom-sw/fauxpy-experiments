import re
from pathlib import Path

import common

INPUTS = {}
WORKSPACE = {}

OUTPUT_DIRECTORY_NAME = "selected"


def are_equal_list_items(list_items):
    for item_a in list_items:
        for item_b in list_items:
            if item_a != item_b:
                return False

    return True


def get_pytest_match(content, pattern):
    regex = re.compile(pattern)
    matches = regex.findall(content)
    return matches


def extract_matches(matches, number_of_targets):
    assert number_of_targets >= 1

    if number_of_targets == 1:
        if len(matches) == 0:
            return 0
        if len(matches) <= 1 or are_equal_list_items(matches):
            return int(matches[-1])
        else:
            raise Exception("Problem!")
    else:
        print("Multiple test cases!")
        if len(matches) == 0:
            return 0
        return sum(list(
            map(lambda x: int(x),
                matches)
        ))


def get_pytest_info(content: str,
                    number_of_targets: int):
    passed_matches = get_pytest_match(content, fr"(\d+) passed")
    passed = extract_matches(passed_matches, number_of_targets)
    failed_matches = get_pytest_match(content, fr"(\d+) failed")
    failed = extract_matches(failed_matches, number_of_targets)
    error_matches = get_pytest_match(content, fr"(\d+) error")
    error = extract_matches(error_matches, number_of_targets)

    return passed, failed, error


def get_unittest_info(content):
    raise Exception("Not implemented.")


def get_target_tests_info(version_path: Path):
    test_output_stdout = version_path / common.TEST_OUTPUT_FILE_STDOUT
    test_output_stderr = version_path / common.TEST_OUTPUT_FILE_STDERR

    stderr_content = common.read_file_content(test_output_stderr)
    if stderr_content != "":
        print("STDERROR not empty!")

    stdout_content = common.read_file_content(test_output_stdout)

    number_of_targets = common.number_of_target_tests(version_path)

    if ("pytest" in stdout_content and
            ("collected" in stdout_content or
             "test session starts")):
        return get_pytest_info(stdout_content, number_of_targets)
    elif ("unittest" in stdout_content and
          "pytest" not in stdout_content):
        raise Exception("UNITTEST not supported yet!")
        # return get_unittest_info(stdout_content)
    elif ("unittest" not in stdout_content and
          "pytest" not in stdout_content):
        print("Bad test execution!")
        return -1, -1, -1
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
            f_passed > b_passed)


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

    file_path_result = common.get_output_dir(OUTPUT_DIRECTORY_NAME) / f"{INPUTS['BENCHMARK_NAME']}.json"

    common.save_object_to_json({
        "NUM_ACCEPTED": len(accepted_bugs),
        "ACCEPTED": accepted_bugs,
        "NUM_REJECTED": len(rejected_bugs),
        "REJECTED": rejected_bugs
    }, file_path_result)


if __name__ == '__main__':
    main()
