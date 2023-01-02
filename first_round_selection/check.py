import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

INPUTS = {}
GLOBAL_CONSTANTS = {}

# Constants
TEST_OUTPUT_FILE_STDOUT = "bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR = "bugsinpy_test_output_stderr.txt"
VERSION_PREFIX = "bug"
BUGGY_DIR_NAME = "buggy"
FIXED_DIR_NAME = "fixed"

COMPILED_FLAG_FILE = "bugsinpy_compile_flag"
RUN_TEST_FILE_NAME = "bugsinpy_run_test.sh"
OUTPUT_DIR_NAME = "output"

CURRENT_CSV_RECORD_NUMBER = 1


class BenchmarkInfo:
    def __init__(self,
                 buggy_failed: int,
                 buggy_passed: int,
                 buggy_error: int,
                 fixed_failed: int,
                 fixed_passed: int,
                 fixed_error: int,
                 target_failing_tests: List[str]):
        self.buggy_failed = buggy_failed
        self.buggy_passed = buggy_passed
        self.buggy_error = buggy_error
        self.fixed_failed = fixed_failed
        self.fixed_passed = fixed_passed
        self.fixed_error = fixed_error
        self.target_failing_tests = target_failing_tests

    def is_included(self) -> bool:
        return (self.buggy_failed > 0 and
                self.fixed_passed > 0 and
                self.fixed_error == 0 and
                self.buggy_failed + self.buggy_passed ==
                self.fixed_failed + self.fixed_passed)

    def get_target_failing_tests(self) -> List[str]:
        return self.target_failing_tests


def get_buggy_project_path(bug_number: int):
    return (Path(GLOBAL_CONSTANTS["WORKSPACE_PATH"]) /
            f"{INPUTS['BENCHMARK_NAME']}" /
            f"{VERSION_PREFIX}{bug_number}" /
            BUGGY_DIR_NAME /
            INPUTS["BENCHMARK_NAME"])


def get_fixed_project_path(bug_number: int):
    return (Path(GLOBAL_CONSTANTS["WORKSPACE_PATH"]) /
            f"{INPUTS['BENCHMARK_NAME']}" /
            f"{VERSION_PREFIX}{bug_number}" /
            FIXED_DIR_NAME /
            INPUTS["BENCHMARK_NAME"])


def get_match(content, pattern):
    """
    Probably, benchmark specific.
    """

    reg_pattern = fr"(\d) {pattern}"
    regex = re.compile(reg_pattern)
    matches = regex.findall(content)
    assert len(matches) <= 1
    return 0 if len(matches) == 0 else int(matches[-1])


def get_test_info(version_path: Path) -> Tuple[int, int, int]:
    """
    Probably, benchmark specific.
    """
    test_output_stdout = version_path / TEST_OUTPUT_FILE_STDOUT
    test_output_stderr = version_path / TEST_OUTPUT_FILE_STDERR

    stderr_content = read_file_content(test_output_stderr)
    assert stderr_content == ""

    stdout_content = read_file_content(test_output_stdout)

    failed = get_match(stdout_content, "failed")
    passed = get_match(stdout_content, "passed")
    error = get_match(stdout_content, "error")

    return failed, passed, error


def get_target_failing_tests(buggy_path):
    """
    Probably, benchmark specific.
    """
    target_failing_tests = []

    with (buggy_path / RUN_TEST_FILE_NAME).open() as file:
        lines = file.readlines()

    for line in lines:
        if line.strip() != "":
            elements = line.split()
            current_tg = elements[1]
            if "[" in current_tg:
                print("Alert! Parametrized target failing test!")
            target_failing_tests.append(current_tg)

    return target_failing_tests


def read_file_content(path):
    with path.open() as file:
        content = file.read()
    return content.strip()


def is_compiled(buggy_path):
    compiled_flag_file_path = buggy_path / COMPILED_FLAG_FILE

    if not compiled_flag_file_path.exists():
        return False

    content = read_file_content(buggy_path / COMPILED_FLAG_FILE)
    return content == "1"


def get_benchmark_info(bug_number: int) -> BenchmarkInfo:
    buggy_path = get_buggy_project_path(bug_number)
    fixed_path = get_fixed_project_path(bug_number)

    assert is_compiled(buggy_path)
    assert is_compiled(fixed_path)

    buggy_failed, buggy_passed, buggy_error = get_test_info(buggy_path)
    fixed_failed, fixed_passed, fixed_error = get_test_info(fixed_path)

    target_failing_tests = get_target_failing_tests(buggy_path)

    benchmark_info = BenchmarkInfo(buggy_failed,
                                   buggy_passed,
                                   buggy_error,
                                   fixed_failed,
                                   fixed_passed,
                                   fixed_error,
                                   target_failing_tests)

    return benchmark_info


def get_accepted_file_path():
    pass


def get_output_dir():
    output_dir = Path(OUTPUT_DIR_NAME)
    if not output_dir.exists():
        output_dir.mkdir()

    return output_dir


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict


def python_list_to_info_list(python_list):
    if len(python_list) == 0:
        return "-"

    info_list = f"{python_list[0]}"
    for item in python_list[1:]:
        info_list += f";\n{item}"

    return info_list


def wrap_in_double_quotes(item: str):
    return f'"{item}"'


def get_csv_accepted_bug(accepted_bug_number, target_failing_tests):
    global CURRENT_CSV_RECORD_NUMBER

    record_csv_format = f'{CURRENT_CSV_RECORD_NUMBER},'\
                        f'{INPUTS["PYTHON_V"]},'\
                        f'{wrap_in_double_quotes(INPUTS["BENCHMARK_NAME"])},'\
                        f'{accepted_bug_number},'\
                        f'{wrap_in_double_quotes(INPUTS["TARGET_DIR"])},'\
                        f'{wrap_in_double_quotes(python_list_to_info_list(INPUTS["TEST_SUITE"]))},'\
                        f'{wrap_in_double_quotes(python_list_to_info_list(INPUTS["EXCLUDE"]))},'\
                        f'{wrap_in_double_quotes(python_list_to_info_list(target_failing_tests))}'
    CURRENT_CSV_RECORD_NUMBER += 1

    return record_csv_format


def save_accepted_bugs_to_file(accepted_bugs_csv_list):
    file_path = get_output_dir() / f"{INPUTS['BENCHMARK_NAME']}_accepted.csv"
    with file_path.open("w") as file:
        for line in accepted_bugs_csv_list:
            file.write(line+"\n")


def save_rejected_bugs_to_file(rejected_bugs_numbers_list):
    file_path = get_output_dir() / f"{INPUTS['BENCHMARK_NAME']}_rejected.csv"
    with file_path.open("w") as file:
        for line in rejected_bugs_numbers_list:
            file.write(line+"\n")


def main():
    global INPUTS, GLOBAL_CONSTANTS

    if len(sys.argv) != 2:
        print("Pass the benchmark info file. For instance:\npython check.py keras.json")
        exit(1)

    INPUTS = load_json_to_dictionary(sys.argv[1])
    GLOBAL_CONSTANTS = load_json_to_dictionary("workspace.json")

    accepted_bugs_csv_list = []
    rejected_bugs_numbers_list = []

    for current_bug_number in range(INPUTS["BUG_NUMBER_START"], INPUTS["BUG_NUMBER_END"] + 1):
        print(f"{INPUTS['BENCHMARK_NAME']}{current_bug_number}")
        benchmark_info = get_benchmark_info(current_bug_number)
        if benchmark_info.is_included():
            print("Accepted")
            accepted = get_csv_accepted_bug(current_bug_number, benchmark_info.get_target_failing_tests())
            accepted_bugs_csv_list.append(accepted)
        else:
            print("Rejected")
            rejected_bugs_numbers_list.append(current_bug_number)

    save_accepted_bugs_to_file(accepted_bugs_csv_list)
    save_rejected_bugs_to_file(rejected_bugs_numbers_list)


if __name__ == '__main__':
    main()
