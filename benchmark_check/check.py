"""
This script performs the following checks:
1. The test fails on the buggy version.
2. The test passes on the fixed version.
3. The test does not result in an error in either the buggy or the fixed version.
Having errors in the buggy version while having also failing tests is OK.
But not errors in the fixed version.

Then, it generates a csv file to be tests by the bash script generator.
Although, customizing the test suite is still manual.
This script only returns the whole test suite.
"""

import re
from pathlib import Path
from typing import List, Tuple

BENCHMARK_NAME = "keras"
BUG_NUMBER_START = "1"
BUG_NUMBER_END = "10"
WORKSPACE_PATH = "/home/moe/BugsInPyExp/7.keras"
TEST_OUTPUT_FILE_STDOUT = "bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR = "bugsinpy_test_output_stderr.txt"

VERSION_PREFIX = "bug"
BUGGY_DIR_NAME = "buggy"
FIXED_DIR_NAME = "fixed"
COMPILED_FLAG_FILE = "bugsinpy_compile_flag"
RUN_TEST_FILE_NAME = "bugsinpy_run_test.sh"


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
    return Path(WORKSPACE_PATH) / f"{VERSION_PREFIX}{bug_number}" / BUGGY_DIR_NAME / BENCHMARK_NAME


def get_fixed_project_path(bug_number: int):
    return Path(WORKSPACE_PATH) / f"{VERSION_PREFIX}{bug_number}" / FIXED_DIR_NAME / BENCHMARK_NAME


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
            target_failing_tests.append(elements[1])

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


def add_benchmark(info):
    pass


def remove_benchmark(info):
    pass


def main():
    for i in range(int(BUG_NUMBER_START), int(BUG_NUMBER_END) + 1):
        print(f"{BENCHMARK_NAME}{i}")
        benchmark_info = get_benchmark_info(i)
        if benchmark_info.is_included():
            add_benchmark(benchmark_info)
        else:
            print("Removed")
            remove_benchmark(benchmark_info)


if __name__ == '__main__':
    main()
