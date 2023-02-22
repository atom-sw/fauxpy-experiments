import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple, List

from github import Github
from github import UnknownObjectException, GithubException

import pickle

VERSION_PREFIX = "bug"
BUGGY_DIR_NAME = "buggy"
FIXED_DIR_NAME = "fixed"

TEST_OUTPUT_FILE_STDOUT = "bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR = "bugsinpy_test_output_stderr.txt"

REMOTE_URL_FILE_NAME = "bugsinpy_remote_url.txt"

BUGSINPY_BUG_INFO_FILE_NAME = "bugsinpy_bug.info"

RUN_TEST_FILE_NAME = "bugsinpy_run_test.sh"

WORKSPACE_FILE_NAME = "workspace.json"

CORRECT_TEST_OUTPUT_DIRECTORY_NAME = "correct"

TIME_SELECTED_BUGS_FILE_NAME = "time_selected_bugs.json"

SUBJECT_INFO_DIRECTORY_NAME = "info"

CACHE_DIR_NAME = "cache"

EMPTY_GROUND_TRUTH_FILE_NAME = "empty_ground_truth_info.json"


def read_file_content(path) -> str:
    with path.open() as file:
        content = file.read()
    return content.strip()


def load_json_to_dictionary(file_path: str):
    with open(file_path) as file:
        data_dict = json.load(file)

    return data_dict


GITHUB_TOKEN = read_file_content(Path("github_token.txt"))
WORKSPACE_PATH = load_json_to_dictionary(WORKSPACE_FILE_NAME)["WORKSPACE_PATH"]


def get_output_dir(directory_name: str):
    output_dir = Path(directory_name)
    if not output_dir.exists():
        output_dir.mkdir()

    return output_dir


def get_matches_in_content(content, pattern):
    regex = re.compile(pattern)
    matches = regex.findall(content)
    return matches


def get_buggy_project_path(benchmark_name: str,
                           bug_number: int) -> Path:
    workspace = WORKSPACE_PATH
    return (Path(workspace) /
            f"{benchmark_name}" /
            f"{VERSION_PREFIX}{bug_number}" /
            BUGGY_DIR_NAME /
            benchmark_name)


def get_fixed_project_path(benchmark_name: str,
                           bug_number: int):
    workspace = WORKSPACE_PATH
    return (Path(workspace) /
            f"{benchmark_name}" /
            f"{VERSION_PREFIX}{bug_number}" /
            FIXED_DIR_NAME /
            benchmark_name)


def get_command_line_info_file():
    if len(sys.argv) != 2:
        print("Pass the benchmark info file (e.g., info/keras.json).")
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


def load_correct_test_bugs():
    correct_test_bugs: Dict = {}

    selected_dir_path = Path(CORRECT_TEST_OUTPUT_DIRECTORY_NAME)
    json_files = list(selected_dir_path.rglob("*.json"))
    json_files.sort()
    for file_path in json_files:
        selected_benchmark = load_json_to_dictionary(str(file_path.absolute().resolve()))
        selected_benchmark_name = selected_benchmark["BENCHMARK_NAME"]
        correct_test_bugs[selected_benchmark_name] = selected_benchmark

    return correct_test_bugs


def get_commit_info(benchmark_name: str,
                    bug_num: int) -> Tuple[str, str, str]:
    buggy_project_path = get_buggy_project_path(benchmark_name, bug_num)
    remote_url_file_path = buggy_project_path / REMOTE_URL_FILE_NAME
    bug_info_file_path = buggy_project_path / BUGSINPY_BUG_INFO_FILE_NAME
    remote_url = read_file_content(remote_url_file_path).strip()
    repo_name = remote_url.replace("https://github.com/", "").strip()
    if repo_name.endswith("/"):
        repo_name = repo_name[:-1]
    fixed_commit_number = list(filter(lambda x: "fixed_commit_id" in x,
                                      read_file_content(bug_info_file_path)
                                      .strip()
                                      .splitlines()))[0].split("=")[1].replace('"', '').strip()
    buggy_commit_number = list(filter(lambda x: "buggy_commit_id" in x,
                                      read_file_content(bug_info_file_path)
                                      .strip()
                                      .splitlines()))[0].split("=")[1].replace('"', '').strip()
    return repo_name, fixed_commit_number, buggy_commit_number


def get_changed_modules(benchmark_name: str,
                        bug_num: int) -> List[str]:
    repo_name, fixed_commit_number, _ = get_commit_info(benchmark_name, bug_num)

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    commit = repo.get_commit(fixed_commit_number)
    changed_files = [x.filename for x in commit.files]

    changed_modules = list(filter(lambda x:
                                  x.endswith(".py") and
                                  "test/" not in x and
                                  "tests/" not in x,
                                  changed_files))

    return changed_modules


def api_wait_search(github,
                    function,
                    *args,
                    **kwargs):
    # Code adopted from Souhaila's module
    limits = github.get_rate_limit()
    reset = limits.search.reset.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    seconds = (reset - now).total_seconds()
    print("Rate limit exceeded")
    print(f"Reset is in {seconds:.3g} seconds.")
    if seconds > 0.0:
        print(f"Waiting for {seconds:.3g} seconds...")
        time.sleep(seconds)
        print("Done waiting - resume!")

    ret_fuc = function(*args, **kwargs)
    return ret_fuc


def get_diff_commit(benchmark_name: str,
                    bug_num: int):
    """
    This function gets the diff commit of the given buggy
    version in the BugsInPy framework. It caches
    the results since fetching this much information
    form GitHub using its API makes
    it stop from providing services.
    """
    cache_file_path = CACHE_DIR_NAME / Path(f"{benchmark_name}_{bug_num}")
    if cache_file_path.exists():
        with cache_file_path.open("rb") as file:
            python_none_test_files = pickle.load(file)
        return python_none_test_files

    repo_name, fixed_commit_info, buggy_commit_info = get_commit_info(benchmark_name, bug_num)

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    # repo = api_wait_search(g, g.get_repo, repo_name)
    fixed_commit = repo.get_commit(fixed_commit_info)

    python_none_test_files = list(filter(lambda x:
                                         x.filename.endswith(".py") and
                                         "test/" not in x.filename and
                                         "tests/" not in x.filename,
                                         fixed_commit.files))

    for ind, file in enumerate(python_none_test_files):
        filename = file.filename
        fixed_content = repo.get_contents(filename, ref=fixed_commit_info).decoded_content.decode('utf-8')
        try:
            buggy_content = repo.get_contents(filename, ref=buggy_commit_info).decoded_content.decode('utf-8')
        except UnknownObjectException:
            print("File not found in the buggy version!")
            buggy_content = ""
        except GithubException:
            print("Using sha of the fixed version!")
            buggy_content = repo.get_contents(filename, ref=f"{fixed_commit_info}^").decoded_content.decode('utf-8')

        python_none_test_files[ind].buggy_content = buggy_content
        python_none_test_files[ind].fixed_content = fixed_content

    if not os.path.exists(Path(CACHE_DIR_NAME)):
        os.mkdir(CACHE_DIR_NAME)

    with cache_file_path.open("wb") as file:
        pickle.dump(python_none_test_files, file)

    return python_none_test_files
