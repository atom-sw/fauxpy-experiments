from pathlib import Path

import common

RESULTS_PATH_FILE_NAME = "results_path.json"


def load_results_path(filename):
    results_path_object = common.load_json_to_dictionary(RESULTS_PATH_FILE_NAME)
    return Path(results_path_object["RESULTS_PATH"])


def main():
    results_path = load_results_path(RESULTS_PATH_FILE_NAME)
    x = 1


if __name__ == '__main__':
    main()
