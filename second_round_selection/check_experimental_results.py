import csv
from pathlib import Path

import common
from common import get_result_manager, ResultManager

MANUALLY_REMOVED_CSV_FILE_NAME = "manually_removed_bugs.csv"
MANUALLY_REMOVED_JSON_FILE_NAME = "manually_removed_bugs.json"
MISSING_STATEMENT_RESULT_ITEMS_FILE = "missing_statement_results.txt"
MISSING_FUNCTION_RESULT_ITEMS_FILE = "missing_function_results.txt"


class ProcedureManager:
    ExtExecutedStepsCount = 0
    IntExecutedStepsCount = 0

    def __init__(self):
        self._result_manager = get_result_manager()

    @staticmethod
    def print_list(items):
        for item in items:
            print(item)

    @classmethod
    def _is_active(cls, activate_flag):
        if activate_flag == 1:
            if cls.ExtExecutedStepsCount != 0:
                print("ONLY ONE STEP CAN BE ACTIVE!")
                return False
            cls.ExtExecutedStepsCount += 1
            return activate_flag == 1
        return False

    @classmethod
    def _is_internal_active(cls, activate_flag):
        if activate_flag == 1:
            if cls.IntExecutedStepsCount != 0:
                print("ONLY ONE INTERNAL STEP CAN BE ACTIVE!")
                return False
            cls.IntExecutedStepsCount += 1
            return activate_flag == 1
        return False

    def print_multiple_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_multiple_result_items()
            print("Multiple result items:")
            self.print_list(items)

    def print_multiple_timeout_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_multiple_timeout_items()
            print("Multiple timeout items:")
            self.print_list(items)

    def print_unfixable_timeout_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_unfixable_timeout_result_items()
            print("Unfixable timeout items:")
            self.print_list(items)

    def remove_bugs_of_unfixable_timeout_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_unfixable_timeout_result_items()
            for item in items:
                self._result_manager.remove_bug_from_results_and_timeout(item.get_project_name(), item.get_bug_number())

    def print_corrupted_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_corrupted_result_items()
            print("Corrupted result items:")
            self.print_list(items)

    def remove_corrupted_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_corrupted_result_items()
            for item in items:
                self._result_manager.remove_result_item(item)

    def print_fishy_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_fishy_result_items()
            print("Fishy result items:")
            self.print_list(items)

    def remove_fishy_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_fishy_result_items()
            for item in items:
                self._result_manager.remove_result_item(item)

    def print_fixable_timeout_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_fixable_timeout_result_items()
            print("Fixable timeout items:")
            self.print_list(items)

    def remove_fixable_timeout_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_fixable_timeout_result_items()
            for item in items:
                self._result_manager.remove_timeout_item(item)

    def print_floating_result_items(self, activate_flag: int):
        if self._is_internal_active(activate_flag):
            items = self._result_manager.get_floating_result_items()
            print("Floating result items:")
            self.print_list(items)

    def remove_floating_result_items(self, activate_flag: int):
        if self._is_internal_active(activate_flag):
            items = self._result_manager.get_floating_result_items()
            for item in items:
                self._result_manager.remove_result_item(item)

    def print_floating_timeout_items(self, activate_flag: int):
        if self._is_internal_active(activate_flag):
            items = self._result_manager.get_floating_timeout_items()
            print("Floating timeout items:")
            self.print_list(items)

    def remove_floating_timeout_items(self, activate_flag: int):
        if self._is_internal_active(activate_flag):
            items = self._result_manager.get_floating_timeout_items()
            for item in items:
                self._result_manager.remove_result_item(item)

    def print_missing_statement_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_missing_statement_result_items()
            print("Missing statement result items:")
            self.print_list(items)

    def save_file_missing_statement_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_missing_statement_result_items()
            print("Saving missing statement result items:")
            missing_items_string = ""
            for item in items:
                missing_items_string += f"{item.get_experiment_id()} "
            common.save_string_to_file(missing_items_string, Path(MISSING_STATEMENT_RESULT_ITEMS_FILE))

    def save_file_missing_function_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_missing_function_result_items()
            print("Saving missing function result items:")
            missing_items_string = ""
            for item in items:
                missing_items_string += f"{item.get_experiment_id()} "
            common.save_string_to_file(missing_items_string, Path(MISSING_FUNCTION_RESULT_ITEMS_FILE))

    def print_missing_function_result_items(self, activate_flag: int):
        if self._is_active(activate_flag):
            items = self._result_manager.get_missing_function_result_items()
            print("Missing function result items:")
            self.print_list(items)

    def generate_manually_removed_json_file(self, activate_flag: int):
        if self._is_active(activate_flag):
            dict_object = {}
            with open(MANUALLY_REMOVED_CSV_FILE_NAME, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for row in csv_reader:
                    benchmark_name = row[0]
                    bug_number = int(row[1])
                    if benchmark_name not in dict_object.keys():
                        dict_object[benchmark_name] = []
                    assert bug_number not in dict_object[benchmark_name]
                    dict_object[benchmark_name].append(bug_number)
                    dict_object[benchmark_name].sort()

            common.save_object_to_json(dict_object, Path(MANUALLY_REMOVED_JSON_FILE_NAME))

    def generate_scripts(self, activate_flag: int):
        if self._is_active(activate_flag):
            # Step 1.1: Go to script generation phase. Generate new scripts.
            pass

            # Step 2.2: Print floating results.
            self.print_floating_result_items(0)

            # Step 3.3: Put them to garbage.
            self.remove_floating_result_items(0)

            # Step 4.4: Print floating timeout items.
            self.print_floating_timeout_items(0)

            # Step 5.5: Put them to garbage.
            self.remove_floating_timeout_items(0)


def main():
    """
    Rule 1: Steps having pass as code are manual.
    Rule 2: Only one automated step must be active (pass 1 to activate) at each run.
    Rule 3: If more than one automated step is active, the first
     one runs and the script complains.
    Rule 4: Steps must be taken in order.
    """

    procedure_manager = ProcedureManager()

    # Step 1.1: Print multiple result items.
    procedure_manager.print_multiple_result_items(0)

    # Step 1.2: Move to garbage the older ones.
    pass

    # Step 2.1: Print multiple timeout items.
    procedure_manager.print_multiple_timeout_items(0)

    # Step 2.2: Move to garbage the older ones.
    pass

    # Step 3.1: Print unfixable timeout items.
    procedure_manager.print_unfixable_timeout_items(0)

    # Step 3.2: If timeout out due to server problem
    # put timeout to garbage.
    # Delete redundant result from before.

    # Step 3.3: Put their info in manually_removed_bugs.csv.
    pass

    # Step 3.4: Remove their buggy version from info.csv in script generation phase.
    pass

    # Step 3.5: Put to garbage the results and timeouts of their 7 experiments.
    procedure_manager.remove_bugs_of_unfixable_timeout_items(0)

    # Step 4.1: Print corrupted result items:
    procedure_manager.print_corrupted_result_items(0)

    # Step 4.3: Put to garbage results and timeouts
    # of those happening due to bugs in server.
    # Delete redundant result from before.
    pass

    # Step: 4.2:
    # - For fixable ones, skip for now.
    # - For those happening because of bugs in tool, take note.
    # - For unfixable ones:
    #       * Put their info in the removed bugs csv file.
    #       * Put to garbage the results and timeouts of their 7 experiments.
    #       * Remove their bugs from info.csv in script generation phase.
    pass

    # Step 5.1: Print fishy result items:
    procedure_manager.print_fishy_result_items(0)

    # Step 5.2:
    # - For correct ones, add their id to correct fishy file.
    # - For fixable ones, skip for now.
    # - For those happening because of bugs in tool, take note.
    # - For unfixable ones:
    #       * Delete redundant results and their timeouts from before.
    #       IF NOT REDUNDANT:
    #       * Put their info in manually_removed_bugs.csv.
    #       * Put to garbage the results and timeouts of their 7 experiments.
    #       * Remove their bugs from info.csv in script generation phase.
    pass

    # Step 6.1: Print fixable timeout items.
    procedure_manager.print_fixable_timeout_items(0)

    # Step 6.2: For fixable ones, skip for now.
    pass

    # Step 6.3: For unfixable ones:
    # - Delete redundant ones from before.
    # If not redundant:
    # - Put their info in the removed bugs csv file.
    # - Put to garbage the results and timeouts of their 7 experiments.
    # - Remove their bugs from info.csv in script generation phase.
    pass

    # Step 7.1: Print corrupted result items again:
    procedure_manager.print_corrupted_result_items(0)

    # Step 7.2: They must all be fixable:
    # - Fix them.
    pass

    # Step 7.3: Put to garbage their results.
    procedure_manager.remove_corrupted_result_items(0)

    # Step 8.1: Print fishy result items again:
    procedure_manager.print_fishy_result_items(0)

    # Step 8.2: They must all be fixable:
    # - Fix them.
    pass

    # Step 8.3: Put to garbage their results.
    procedure_manager.remove_fishy_result_items(0)

    # Step 9.1: Print fixable timeout items.
    procedure_manager.print_fixable_timeout_items(0)

    # Step 9.2: They must all be fixable:
    # - Set their timeouts to 48 hrs in script generation phase.
    pass

    # Step 9.3: Put them to garbage.
    procedure_manager.remove_fixable_timeout_items(0)

    # Step 10: See the code of generate_scripts function (the function below).
    procedure_manager.generate_scripts(0)

    # Step 11.1: Print missing statement result items.
    procedure_manager.print_missing_statement_result_items(0)

    # Step 11.2: Save missing statement result items' ids horizontally.
    procedure_manager.save_file_missing_statement_result_items(0)

    # Step 11.3: Print missing function result items (only for Stack Trace).
    procedure_manager.print_missing_function_result_items(0)

    # Step 11.4: Save missing function result items' ids horizontally (only for Stack Trace).
    procedure_manager.save_file_missing_function_result_items(0)

    # Step 11.5: Add them to the experiments batch.
    pass

    # Step 12.1: Generate manually removed json file.
    procedure_manager.generate_manually_removed_json_file(1)

    # Step 12.2: Send it to first round selection.
    pass


if __name__ == '__main__':
    main()
