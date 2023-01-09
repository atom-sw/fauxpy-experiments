import json
import sys
from pathlib import Path

VERSION_PREFIX = "bug"
BUGGY_DIR_NAME = "buggy"
FIXED_DIR_NAME = "fixed"

TEST_OUTPUT_FILE_STDOUT = "bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR = "bugsinpy_test_output_stderr.txt"

OUTPUT_DIR_NAME = "output"

WORKSPACE_FILE_NAME = "workspace.json"


def get_output_dir():
    output_dir = Path(OUTPUT_DIR_NAME)
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


def get_project_info_file_path():
    if len(sys.argv) != 2:
        print("Pass the benchmark info file. For instance:\npython check.py keras.json")
        exit(1)

    return Path(sys.argv[1])
