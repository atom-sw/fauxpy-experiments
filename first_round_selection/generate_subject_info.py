from pathlib import Path
from typing import List, Dict, Tuple
from github import Github

import common

INFO = {}
SELECTED = {}
WORKSPACE_PATH: str = ""
SUBJECT_INFO_CSV_FILE_NAME = "subject_info.csv"

REMOTE_URL_FILE_NAME = "bugsinpy_remote_url.txt"

BUGSINPY_BUG_INFO_FILE_NAME = "bugsinpy_bug.info"

GITHUB_TOKEN = common.read_file_content(Path("github_token.txt"))


def load_info():
    global SELECTED
    global INFO
    global WORKSPACE_PATH

    SELECTED = common.load_json_to_dictionary(common.TIME_SELECTED_BUGS_FILE_NAME)
    del SELECTED["NUM_BUGS"]
    del SELECTED["TIME_ESTIMATION_HOURS"]
    del SELECTED["TIME_ESTIMATION_DAYS"]
    del SELECTED["TIME_ESTIMATION_WEEKS"]

    json_files = list(Path(common.SUBJECT_INFO_DIRECTORY_NAME).rglob("*.json"))
    json_files.sort()
    for item in json_files:
        benchmark_info = common.load_json_to_dictionary(str(item.absolute().resolve()))
        INFO[benchmark_info["BENCHMARK_NAME"]] = benchmark_info

    WORKSPACE_PATH = common.load_json_to_dictionary(common.WORKSPACE_FILE_NAME)["WORKSPACE_PATH"]


def unittest_to_pytest(item):
    elements = item.split(".")
    if len(elements) == 4:
        return f"{elements[0]}/{elements[1]}.py::{elements[2]}::{elements[3]}"
    elif len(elements) == 5:
        return f"{elements[0]}/{elements[1]}/{elements[2]}.py::{elements[3]}::{elements[4]}"
    else:
        raise Exception("Problem!")


def get_generalized_test(item):
    return item.split("[")[0]


def get_reformatted_target_failing_tests(original_target_tests: List[str]) -> List[str]:
    reformatted_target_tests = []

    for item in original_target_tests:
        generalized_original = get_generalized_test(item)
        if "/" in generalized_original.lower() and ".py" in generalized_original.lower():
            reformatted_target_tests.append(generalized_original)
        else:
            assert "/" not in generalized_original.lower()
            assert ".py" not in generalized_original.lower()

            generalized_original = unittest_to_pytest(generalized_original)
            reformatted_target_tests.append(generalized_original)

        # if item != generalized_original:
        #     print("Reformat test")
        #     print(item)
        #     print(generalized_original)
        #     print("------------")

    return reformatted_target_tests


def get_target_failing_tests(benchmark_name: str,
                             bug_num: int) -> List[str]:
    buggy_path = common.get_buggy_project_path(WORKSPACE_PATH, benchmark_name, bug_num)
    run_test_file_path = buggy_path / common.RUN_TEST_FILE_NAME

    content = common.read_file_content(run_test_file_path)

    target_tests_in_content = list(filter(
        lambda x: x.lower().startswith("test") or
                  x.lower().startswith("tests") or
                  x.lower().startswith("pandas/tests") or
                  x.lower().startswith("pandas/test") or
                  x.lower().startswith("spacy/tests") or
                  x.lower().startswith("spacy/test") or
                  x.lower().startswith("tornado.test") or
                  x.lower().startswith("tornado.tests") or
                  x.lower().startswith("tqdm/tests") or
                  x.lower().startswith("tqdm/test"), content.split()))

    target_failing_tests = get_reformatted_target_failing_tests(target_tests_in_content)

    return target_failing_tests


def get_commit_info(benchmark_name: str,
                    bug_num: int) -> Tuple[str, str]:
    buggy_project_path = common.get_buggy_project_path(WORKSPACE_PATH, benchmark_name, bug_num)
    remote_url_file_path = buggy_project_path / REMOTE_URL_FILE_NAME
    bug_info_file_path = buggy_project_path / BUGSINPY_BUG_INFO_FILE_NAME
    remote_url = common.read_file_content(remote_url_file_path).strip()
    repo_name = remote_url.replace("https://github.com/", "").strip()
    if repo_name.endswith("/"):
        repo_name = repo_name[:-1]
    fixed_commit_number = list(filter(lambda x: "fixed_commit_id" in x,
                                      common.read_file_content(bug_info_file_path)
                                      .strip()
                                      .splitlines()))[0].split("=")[1].replace('"', '').strip()
    return repo_name, fixed_commit_number


def get_changed_modules(benchmark_name: str,
                        bug_num: int) -> List[str]:
    repo_name, fixed_commit_number = get_commit_info(benchmark_name, bug_num)

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


# Only used for analysis. Not in the pipeline.
def get_target_dir(benchmark_name: str,
                   bug_num: int):
    default_target_dir = INFO[benchmark_name]["TARGET_DIR"]

    if default_target_dir == ".":
        return "."

    changed_modules = get_changed_modules(benchmark_name, bug_num)

    target_dir = INFO[benchmark_name]["TARGET_DIR"]
    for item in changed_modules:
        if not item.startswith(target_dir):
            print(benchmark_name, bug_num)
            print(item)


# These three (among the 320) had target directories other
# than the default ones. So, we changed their json
# information files.
# keras 9
# docs/autogen.py
# sanic 1
# examples/blueprint_middlware_execution_order.py
# sanic/app.py
# spacy 3
# bin/wiki_entity_linking/wikipedia_processor.py
def get_subject_info_for_bug(benchmark_name: str,
                             bug_num: int):
    target_failing_tests = get_target_failing_tests(benchmark_name, bug_num)
    # get_target_dir(benchmark_name, bug_num)

    record = {
        "PYTHON_V": INFO[benchmark_name]["PYTHON_V"],
        "BENCHMARK_NAME": benchmark_name,
        "BUG_NUMBER": bug_num,
        "TARGET_DIR": INFO[benchmark_name]["TARGET_DIR"],
        "TEST_SUITE": INFO[benchmark_name]["TEST_SUITE"],
        "EXCLUDE": INFO[benchmark_name]["EXCLUDE"],
        "TARGET_FAILING_TESTS": target_failing_tests
    }

    return record


def get_subject_infos_for_benchmark(benchmark_name: str,
                                    bugs: List[int]):
    subject_infos_for_benchmark = []

    for bug_num in bugs:
        subject_info_for_bug = get_subject_info_for_bug(benchmark_name, bug_num)
        subject_infos_for_benchmark.append(subject_info_for_bug)

    return subject_infos_for_benchmark


def python_list_to_info_list(python_list):
    if len(python_list) == 0:
        return "-"

    info_list = f"{python_list[0]}"
    for item in python_list[1:]:
        info_list += f";\n{item}"

    return info_list


def wrap_in_double_quotes(item: str):
    return f'"{item}"'


def get_csv_row(row_num, row_info):
    record_csv_format = f'{row_num},' \
                        f'{row_info["PYTHON_V"]},' \
                        f'{row_info["BENCHMARK_NAME"]},' \
                        f'{row_info["BUG_NUMBER"]},' \
                        f'{row_info["TARGET_DIR"]},' \
                        f'{wrap_in_double_quotes(python_list_to_info_list(row_info["TEST_SUITE"]))},' \
                        f'{wrap_in_double_quotes(python_list_to_info_list(row_info["EXCLUDE"]))},' \
                        f'{wrap_in_double_quotes(python_list_to_info_list(row_info["TARGET_FAILING_TESTS"]))}'

    return record_csv_format


def produce_row_number(row_info):
    benchmark_names = list(INFO.keys())
    ind = benchmark_names.index(row_info["BENCHMARK_NAME"])
    row_number = (ind + 1) * 1000 + row_info["BUG_NUMBER"]

    return row_number


def save_subject_info_list_as_csv(row_infos: List[Dict]):
    csv_rows: List[str] = []
    for index, row_info in enumerate(row_infos):
        row_number = produce_row_number(row_info)
        csv_row = get_csv_row(row_number, row_info)
        csv_rows.append(csv_row)

    with open(SUBJECT_INFO_CSV_FILE_NAME, "w") as file:
        file.write("#,PYTHON_V,BENCHMARK_NAME,BUG_NUMBER,TARGET_DIR,TEST_SUITE,EXCLUDE,TARGET_FAILING_TESTS\n")
        for csv_r in csv_rows:
            file.write(csv_r + "\n")


def main():
    load_info()

    all_subject_infos = []

    for benchmark_name, bugs in SELECTED.items():
        subject_infos_for_benchmark = get_subject_infos_for_benchmark(benchmark_name, bugs)
        all_subject_infos += subject_infos_for_benchmark

    common.save_object_to_json(all_subject_infos, Path("subject_info.json"))
    save_subject_info_list_as_csv(all_subject_infos)


# Only used for analysis. Not in the pipeline.
def checking():
    load_info()

    for benchmark_name, bugs in SELECTED.items():
        if benchmark_name == "spacy":
            # subject_infos_for_benchmark = get_subject_infos_for_benchmark(benchmark_name, bugs)
            for bug_num in bugs:
                buggy_path = common.get_buggy_project_path(WORKSPACE_PATH, benchmark_name, bug_num)
                if (buggy_path / "spacy/tests").exists():
                    print("tests")
                if (buggy_path / "spacy/test").exists():
                    print("!!!!!!!!!!!")
                if (buggy_path / "tests").exists():
                    print("!!!!!!!!!!!")
                if (buggy_path / "test").exists():
                    print("!!!!!!!!!!!")


if __name__ == '__main__':
    main()
    # checking()