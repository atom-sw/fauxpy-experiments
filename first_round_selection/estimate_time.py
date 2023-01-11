import csv
import random
from pathlib import Path
from typing import Dict

import common

# Parameters
# -----------
NUM_NODES = 15

# Pick these at least
CONSTANT_NUM_BUG_PER_PROJECT = 10

# If there is time left, pick more randomly until reaching this
MAX_DAYS = 14
# -----------

# Constants
TIMEOUT_FILE = "timeout_info.csv"
SBFL = "sbfl"
MBFL = "mbfl"
PS = "ps"
ST = "st"
STATEMENT = "statement"
FUNCTION = "function"

MAX_HR = MAX_DAYS * 24

FIRST_ROUND_BUGS_INFO: Dict = {}


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


def load_first_round_selected_bugs_info():
    global FIRST_ROUND_BUGS_INFO

    selected_dir_path = Path(common.SELECTED_OUTPUT_DIRECTORY_NAME)

    for file_path in selected_dir_path.rglob("*.json"):
        selected_benchmark = common.load_json_to_dictionary(str(file_path.absolute().resolve()))
        selected_benchmark_name = selected_benchmark["BENCHMARK_NAME"]
        FIRST_ROUND_BUGS_INFO[selected_benchmark_name] = selected_benchmark


def get_time_for_benchmark(benchmark_name: str):
    sbfl_time = get_experiment_timeout(benchmark_name, SBFL)
    mbfl_time = get_experiment_timeout(benchmark_name, MBFL)
    ps_time = get_experiment_timeout(benchmark_name, PS)
    st_time = get_experiment_timeout(benchmark_name, ST)

    return sbfl_time * 2 + mbfl_time * 2 + ps_time * 2 + st_time


def select_bugs(benchmark_info, num_bugs_per_benchmark, is_random=False):
    selected_bugs = []
    benchmark_name = benchmark_info["BENCHMARK_NAME"]

    if is_random:
        if len(benchmark_info["ACCEPTED"]) > 0:
            rand_index = random.randint(0, len(benchmark_info["ACCEPTED"]) - 1)
            selected_bugs.append(benchmark_info["ACCEPTED"][rand_index])
    else:
        for index, item in enumerate(benchmark_info["ACCEPTED"]):
            if index < min(benchmark_info["NUM_ACCEPTED"], num_bugs_per_benchmark):
                selected_bugs.append(item)

    for item in selected_bugs:
        FIRST_ROUND_BUGS_INFO[benchmark_name]["ACCEPTED"].remove(item)
        FIRST_ROUND_BUGS_INFO[benchmark_name]["NUM_ACCEPTED"] -= 1

    return selected_bugs


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


def main():
    load_first_round_selected_bugs_info()
    selected_bugs_info = {}

    for benchmark in FIRST_ROUND_BUGS_INFO.values():
        constant_bugs = select_bugs(benchmark, CONSTANT_NUM_BUG_PER_PROJECT)
        selected_bugs_info[benchmark["BENCHMARK_NAME"]] = constant_bugs

    needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)
    available_time = MAX_HR

    while needed_time < MAX_HR:
        print("Needed time: ", needed_time)
        print("Available time: ", available_time)
        print("Calc more")
        for benchmark in FIRST_ROUND_BUGS_INFO.values():
            constant_bugs = select_bugs(benchmark, 1, True)
            selected_bugs_info[benchmark["BENCHMARK_NAME"]] += constant_bugs
            needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)

            if needed_time >= available_time:
                break

        print("---------------")

    needed_time = (get_needed_time(selected_bugs_info)) / float(NUM_NODES)
    print("Final needed time: ", needed_time)
    print("Available time: ", available_time)

    selected_bugs_info["NUM_BUGS"] = get_num_bugs(selected_bugs_info)
    selected_bugs_info["TIME_ESTIMATION_HOURS"] = needed_time
    selected_bugs_info["TIME_ESTIMATION_DAYS"] = needed_time / 24
    selected_bugs_info["TIME_ESTIMATION_WEEKS"] = needed_time / (24 * 7)
    common.save_object_to_json(selected_bugs_info, Path("time_selected_bugs.json"))


if __name__ == '__main__':
    main()
