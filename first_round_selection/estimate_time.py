import csv
import random
from pathlib import Path
from typing import Dict, Optional

import common

# Parameters
# -----------
NUM_NODES = 15

MAX_DAYS = 14
# -----------

# Constants
TIMEOUT_FILE = "timeout_info.csv"
MANUALLY_REMOVED_BUGS_FILE_NAME = "manually_removed_bugs.json"

SBFL = "sbfl"
MBFL = "mbfl"
PS = "ps"
ST = "st"

STATEMENT = "statement"
FUNCTION = "function"

MAX_HR = MAX_DAYS * 24

CORRECT_TEST_BUGS_INFO: Dict = {}

random.seed(13658)


def read_csv_as_dict_list(file_path):
    subject_info_table = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subject_info_table.append(row)

    return subject_info_table


def get_experiment_timeout(benchmark_name, family) -> int:
    timeout_info = read_csv_as_dict_list(TIMEOUT_FILE)

    benchmark_timeout_info = list(filter(lambda x: x["BENCHMARK_NAME"] == benchmark_name, timeout_info))[0]
    experiment_timeout = benchmark_timeout_info[family]

    return int(experiment_timeout)


def get_time_for_benchmark(benchmark_name: str):
    sbfl_time = get_experiment_timeout(benchmark_name, SBFL)
    mbfl_time = get_experiment_timeout(benchmark_name, MBFL)
    ps_time = get_experiment_timeout(benchmark_name, PS)
    st_time = get_experiment_timeout(benchmark_name, ST)

    return sbfl_time * 2 + mbfl_time * 2 + ps_time * 2 + st_time


def pop_bug_randomly(benchmark_info) -> Optional[int]:
    benchmark_name = benchmark_info["BENCHMARK_NAME"]

    if len(benchmark_info["ACCEPTED"]) > 0:
        rand_index = random.randint(0, len(benchmark_info["ACCEPTED"]) - 1)
        selected_bug = benchmark_info["ACCEPTED"][rand_index]
        CORRECT_TEST_BUGS_INFO[benchmark_name]["ACCEPTED"].remove(selected_bug)
        CORRECT_TEST_BUGS_INFO[benchmark_name]["NUM_ACCEPTED"] -= 1
        return selected_bug

    return None


def get_needed_time(second_round_info):
    needed_time = 0

    for key, value in second_round_info.items():
        needed_time += get_time_for_benchmark(key) * len(value)

    return needed_time


def get_num_bugs(selected_bugs_info):
    num_bugs = 0
    for item in selected_bugs_info.values():
        num_bugs += len(item)

    return num_bugs


def num_bug_left():
    count_of_remaining = 0
    for item in CORRECT_TEST_BUGS_INFO.values():
        count_of_remaining += item["NUM_ACCEPTED"]

    return count_of_remaining


def replace_items(selected_bugs_info: Dict,
                  empty_ground_truth_bugs_info: Dict,
                  manually_removed_bugs_info: Dict):
    removed_bugs_info = {}
    items_1 = empty_ground_truth_bugs_info.items()
    items_2 = manually_removed_bugs_info.items()

    # TODO: Here
    pass


def main():
    global CORRECT_TEST_BUGS_INFO

    CORRECT_TEST_BUGS_INFO = common.load_correct_test_bugs()
    empty_ground_truth_bugs_info = common.load_json_to_dictionary(common.EMPTY_GROUND_TRUTH_FILE_NAME)
    manually_removed_bugs_info = common.load_json_to_dictionary(MANUALLY_REMOVED_BUGS_FILE_NAME)

    selected_bugs_info = {}

    for benchmark in CORRECT_TEST_BUGS_INFO.values():
        selected_bugs_info[benchmark["BENCHMARK_NAME"]] = []

    needed_time = 0
    available_time = MAX_HR

    while needed_time < MAX_HR:
        print("Needed time: ", needed_time)
        print("Available time: ", available_time)
        print("Calc more")
        print("---------------")
        for benchmark in CORRECT_TEST_BUGS_INFO.values():
            bug = pop_bug_randomly(benchmark)
            if bug is not None:
                selected_bugs_info[benchmark["BENCHMARK_NAME"]].append(bug)
                selected_bugs_info[benchmark["BENCHMARK_NAME"]].sort()
                needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)
                if needed_time >= available_time:
                    break
        bug_left = num_bug_left()
        print(bug_left)
        if bug_left == 0:
            break

    replace_items(selected_bugs_info, empty_ground_truth_bugs_info, manually_removed_bugs_info)

    needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)
    print("Final needed time: ", needed_time)
    print("Available time: ", available_time)

    selected_bugs_info["NUM_BUGS"] = get_num_bugs(selected_bugs_info)
    selected_bugs_info["TIME_ESTIMATION_HOURS"] = needed_time
    selected_bugs_info["TIME_ESTIMATION_DAYS"] = needed_time / 24
    selected_bugs_info["TIME_ESTIMATION_WEEKS"] = needed_time / (24 * 7)
    common.save_object_to_json(selected_bugs_info, Path(common.TIME_SELECTED_BUGS_FILE_NAME))


if __name__ == '__main__':
    main()
