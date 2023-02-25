from pathlib import Path
from typing import List, Tuple

from common import ScriptItem, ResultItem, TimeoutItem, PathManager, ResultManager

PATH_ITEMS_FILE_NAME = "path_items.json"


def load_script_items(scripts_path: Path) -> List[ScriptItem]:
    script_items = []
    for script_path in scripts_path.iterdir():
        script_object = ScriptItem(str(script_path.name))
        script_items.append(script_object)
    script_items.sort(key=lambda x: x.get_experiment_id())
    return script_items


def load_result_timeout_items(results_path: Path) -> Tuple[List[ResultItem], List[TimeoutItem]]:
    result_items = []
    timeout_items = []

    for result_path in results_path.iterdir():
        if result_path.name != "Timeouts":
            result_object = ResultItem(result_path)
            result_items.append(result_object)
    result_items.sort(key=lambda x: x.get_experiment_id())

    timeouts_path = results_path / "Timeouts"
    for timeout_path in timeouts_path.iterdir():
        timeout_object = TimeoutItem(timeout_path)
        timeout_items.append(timeout_object)
    timeout_items.sort(key=lambda x: x.get_experiment_id())

    return result_items, timeout_items


def main():
    path_manager = PathManager(PATH_ITEMS_FILE_NAME)
    results_path = path_manager.get_results_path()
    scripts_path = path_manager.get_scripts_path()

    result_items, timeout_items = load_result_timeout_items(results_path)
    script_items = load_script_items(scripts_path)
    result_manager = ResultManager(result_items, timeout_items, script_items)

    # multiple_result_items = result_manager.get_multiple_result_items()
    # print("Multiple result items:")
    # for item in multiple_result_items:
    #     print(item)

    # multiple_timeout_items = result_manager.get_multiple_timeout_items()
    # print("Multiple timeout items:")
    # for item in multiple_timeout_items:
    #     print(item)

    # corrupted_result_items = result_manager.get_corrupted_result_items()
    # print("Corrupted result items:")
    # for item in corrupted_result_items:
    #     print(item)

    # fishy_result_items = result_manager.get_fishy_result_items()
    # print("Fishy result items:")
    # for item in fishy_result_items:
    #     print(item)

    # normal_result_items = result_manager.get_normal_result_items()
    # print("Normal result items:")
    # for item in normal_result_items:
    #     print(item)

    missing_statement_result_items = result_manager.get_missing_statement_result_items()
    print("Missing statement result items:")
    for item in missing_statement_result_items:
        print(item)


if __name__ == '__main__':
    main()
