from pathlib import Path
from typing import List

from common import ScriptItem, PathManager

PATH_ITEMS_FILE_NAME = "path_items.json"


def load_script_items(scripts_path: Path) -> List[ScriptItem]:
    script_items = []
    for script_path in scripts_path.iterdir():
        script_object = ScriptItem(str(script_path.name))
        script_items.append(script_object)
    script_items.sort(key=lambda x: x.get_experiment_id())
    return script_items


def main():
    path_manager = PathManager(PATH_ITEMS_FILE_NAME)

    scripts_path = path_manager.get_scripts_path()
    results_path = path_manager.get_results_path()

    script_items = load_script_items(scripts_path)
    # result_items = load_result_items(results_path)

    for script_item in script_items:
        print(script_item)

    x = 1


if __name__ == '__main__':
    main()
