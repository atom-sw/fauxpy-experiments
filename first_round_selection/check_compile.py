import sys

import common

INPUTS = {}

COMPILED_FLAG_FILE = "bugsinpy_compile_flag"


def is_compiled(project_path):
    compiled_flag_file_path = project_path / COMPILED_FLAG_FILE
    env_dir_path = project_path / "env"
    test_run_stdout = project_path / common.TEST_OUTPUT_FILE_STDOUT
    test_run_stderr = project_path / common.TEST_OUTPUT_FILE_STDERR

    for item in [compiled_flag_file_path,
                 env_dir_path,
                 test_run_stdout,
                 test_run_stderr]:
        if not item.exists():
            return False

    content = common.read_file_content(project_path / COMPILED_FLAG_FILE)
    return content == "1"


def compile_check():
    benchmark_name = INPUTS["BENCHMARK_NAME"]
    for current_bug_number in range(INPUTS["BUG_NUMBER_START"], INPUTS["BUG_NUMBER_END"] + 1):
        buggy_path = common.get_buggy_project_path(benchmark_name, current_bug_number)
        fixed_path = common.get_fixed_project_path(benchmark_name, current_bug_number)

        if is_compiled(buggy_path) and is_compiled(fixed_path):
            print(f"OK - {benchmark_name}_{current_bug_number}")
        else:
            print(f"NOT COMPILED - {benchmark_name}_{current_bug_number}")


def get_command_line_info_file():
    if len(sys.argv) != 2:
        print("Pass the benchmark info file (e.g., info/keras.json).")
        exit(1)

    return sys.argv[1]


def main():
    global INPUTS

    project_info_file_path = get_command_line_info_file()

    INPUTS = common.load_json_to_dictionary(project_info_file_path)

    compile_check()


if __name__ == '__main__':
    main()
