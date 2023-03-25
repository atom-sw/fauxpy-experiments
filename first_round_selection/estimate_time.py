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


def pop_bug_randomly(benchmark_name: str) -> Optional[int]:
    accepted_bug_list = CORRECT_TEST_BUGS_INFO[benchmark_name]["ACCEPTED"]
    if len(accepted_bug_list) > 0:
        rand_index = random.randint(0, len(accepted_bug_list) - 1)
        selected_bug = accepted_bug_list[rand_index]
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
    # Combining unwanted items from empty ground truth and manually removed ones.
    combined_removing_bugs_info = dict()
    for correct_key, correct_value in CORRECT_TEST_BUGS_INFO.items():
        removing_values = set()
        if correct_key in empty_ground_truth_bugs_info.keys():
            empty_values = empty_ground_truth_bugs_info[correct_key]
            removing_values.update(empty_values)
        if correct_key in manually_removed_bugs_info.keys():
            manually_values = manually_removed_bugs_info[correct_key]
            removing_values.update(manually_values)
        removing_values_list = list(removing_values)
        removing_values_list.sort()
        combined_removing_bugs_info[correct_key] = removing_values_list

    # Remove unwanted items from CORRECT_TEST_BUGS_INFO.
    for combined_key, combined_value in combined_removing_bugs_info.items():
        correct_value = CORRECT_TEST_BUGS_INFO[combined_key]["ACCEPTED"]
        new_correct_value = list(filter(lambda x: x not in combined_value, correct_value))
        CORRECT_TEST_BUGS_INFO[combined_key]["ACCEPTED"] = new_correct_value
        CORRECT_TEST_BUGS_INFO[combined_key]["NUM_ACCEPTED"] = len(new_correct_value)

    # Replacing unwanted items in selected_bugs_info.
    for selected_key, selected_value in selected_bugs_info.items():
        combined_value = combined_removing_bugs_info[selected_key]
        for item in combined_value:
            if item in selected_value:
                selected_value.remove(item)
                bug = pop_bug_randomly(selected_key)
                if bug is not None:
                    selected_bugs_info[selected_key].append(bug)
                    selected_bugs_info[selected_key].sort()


def select_bugs_randomly(selected_bugs_info: Dict):
    needed_time = 0
    available_time = MAX_HR

    while needed_time < MAX_HR:
        print("Needed time: ", needed_time)
        print("Available time: ", available_time)
        print("Calc more")
        print("---------------")
        for benchmark in CORRECT_TEST_BUGS_INFO.values():
            bug = pop_bug_randomly(benchmark["BENCHMARK_NAME"])
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

    return selected_bugs_info


def select_all_info_2_bugs(selected_bugs_info: Dict,
                           correct_test_bugs_info_2: Dict,
                           manually_removed_bugs_info: Dict):
    # Remove manually removed bugs
    # from correct info_2 bugs.
    for m_r_key, m_r_value in manually_removed_bugs_info.items():
        if m_r_key in correct_test_bugs_info_2.keys():
            for m_r_bug in m_r_value:
                if m_r_bug in correct_test_bugs_info_2[m_r_key]["ACCEPTED"]:
                    correct_test_bugs_info_2[m_r_key]["ACCEPTED"].remove(m_r_bug)
                    correct_test_bugs_info_2[m_r_key]["NUM_ACCEPTED"] -= 1

    # # Add all remaining correct info_2 bugs
    # # to selected bugs list.
    for key, value in correct_test_bugs_info_2.items():
        if value["NUM_ACCEPTED"] > 0:
            selected_bugs_info[key] = value["ACCEPTED"]


def main():
    global CORRECT_TEST_BUGS_INFO

    CORRECT_TEST_BUGS_INFO = common.load_correct_test_bugs()
    empty_ground_truth_bugs_info = common.load_json_to_dictionary(common.EMPTY_GROUND_TRUTH_FILE_NAME)
    manually_removed_bugs_info = common.load_json_to_dictionary(MANUALLY_REMOVED_BUGS_FILE_NAME)

    selected_bugs_info = {}
    for benchmark in CORRECT_TEST_BUGS_INFO.values():
        selected_bugs_info[benchmark["BENCHMARK_NAME"]] = []

    select_bugs_randomly(selected_bugs_info)

    # Since this part is added after we ran some experiments, we
    # cannot just remove bugs from the start, otherwise, the simulation
    # may select totally different bugs as the selection process is
    # random, and we may end up with results we wouldn't use
    # in paper. So, this part is begins after the simulation ends.
    replace_items(selected_bugs_info, empty_ground_truth_bugs_info, manually_removed_bugs_info)

    select_bugs_randomly(selected_bugs_info)

    # To keep the randomly selected bugs as they are,
    # we add this step (which was added later) at the end of the
    # random selection process.
    # For simplicity, we select all of them, because most probably many of
    # them have problems and will be removed.
    correct_test_bugs_info_2 = common.load_correct_test_bugs_2()
    select_all_info_2_bugs(selected_bugs_info, correct_test_bugs_info_2, manually_removed_bugs_info)

    # needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)
    # print("Final needed time: ", needed_time)
    # print("Available time: ", MAX_HR)
    #
    selected_bugs_info["NUM_BUGS"] = get_num_bugs(selected_bugs_info)
    # selected_bugs_info["TIME_ESTIMATION_HOURS"] = needed_time
    # selected_bugs_info["TIME_ESTIMATION_DAYS"] = needed_time / 24
    # selected_bugs_info["TIME_ESTIMATION_WEEKS"] = needed_time / (24 * 7)
    common.save_object_to_json(selected_bugs_info, Path(common.TIME_SELECTED_BUGS_FILE_NAME))


if __name__ == '__main__':
    main()
