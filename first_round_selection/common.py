import json
import sys
from pathlib import Path
from typing import Any

VERSION_PREFIX = "bug"
BUGGY_DIR_NAME = "buggy"
FIXED_DIR_NAME = "fixed"

TEST_OUTPUT_FILE_STDOUT = "bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR = "bugsinpy_test_output_stderr.txt"

RUN_TEST_FILE_NAME = "bugsinpy_run_test.sh"

WORKSPACE_FILE_NAME = "workspace.json"

SELECTED_OUTPUT_DIRECTORY_NAME = "selected"


def get_output_dir(directory_name: str):
    output_dir = Path(directory_name)
    if not output_dir.exists():
        output_dir.mkdir()

    return output_dir


def get_buggy_project_path(workspace: str,
                           benchmark_name: str,
                           bug_number: int):
    return (Path(workspace) /
            f"{benchmark_name}" /
            f"{VERSION_PREFIX}{bug_number}" /
            BUGGY_DIR_NAME /
            benchmark_name)


def get_fixed_project_path(workspace: Path,
                           benchmark_name: str,
                           bug_number: int):
    return (Path(workspace) /
            f"{benchmark_name}" /
            f"{VERSION_PREFIX}{bug_number}" /
            FIXED_DIR_NAME /
            benchmark_name)


def read_file_content(path):
    with path.open() as file:
        content = file.read()
    return content.strip()


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict


def get_command_line_info_file():
    if len(sys.argv) != 2:
        print("Pass the benchmark info file. For instance:\npython check.py keras.json")
        exit(1)

    return Path(sys.argv[1])


def save_string_to_file(content: str,
                        file_path: Path):
    with file_path.open("w") as file:
        file.write(content)


def save_object_to_json(obj: Any,
                        file_path: Path):
    string_object = json.dumps(obj, indent=5)
    save_string_to_file(string_object, file_path)


def number_of_target_tests(version_path):
    content = read_file_content(version_path / RUN_TEST_FILE_NAME)
    tox_count = content.count("tox")
    pytest_count = content.count("pytest")
    unittest_count = content.count("unittest")
    py_test_count = content.count("py.test")
    lines_count = len(content.splitlines())
    assert (sum([tox_count, pytest_count, unittest_count, py_test_count]) ==
            max(tox_count, pytest_count, unittest_count, py_test_count))
    assert max(tox_count, pytest_count, unittest_count, py_test_count) == lines_count
    return lines_count
