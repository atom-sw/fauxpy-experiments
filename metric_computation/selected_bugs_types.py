from pathlib import Path
from typing import List

import file_manager
from csv_score_load_manager import CsvScoreItemLoadManager, FLTechnique, CsvScoreItem


def main():
    path_manager = file_manager.PathManager()
    predicate_bug_info = file_manager.load_json_to_dictionary(path_manager.get_predicate_bug_info_file_name())
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()

    predicate_selected_bug_info = {}
    crashing_selected_bug_info = {}
    st_statement_csv_score_items = list(filter(lambda x: x.get_technique() == FLTechnique.ST,
                                               statement_csv_score_items))
    for statement_item in st_statement_csv_score_items:
        bug_key = statement_item.get_bug_key()
        if len(statement_item.get_scored_entities()) != 0:
            crashing_selected_bug_info[bug_key] = True
        else:
            crashing_selected_bug_info[bug_key] = False

        predicate_selected_bug_info[bug_key] = predicate_bug_info[bug_key]

    file_manager.save_dictionary_to_json(crashing_selected_bug_info,
                                         Path(path_manager.get_crashing_selected_bug_info_file_name()))
    file_manager.save_dictionary_to_json(predicate_selected_bug_info,
                                         Path(path_manager.get_predicate_selected_bug_info_file_name()))


def assign_type_to_selected_bugs(csv_score_items: List[CsvScoreItem],
                                 path_manager: file_manager.PathManager):
    crashing_info = (file_manager.
                     load_json_to_dictionary(path_manager.
                                             get_crashing_selected_bug_info_file_name()))
    predicate_info = (file_manager.
                      load_json_to_dictionary(path_manager.
                                              get_predicate_selected_bug_info_file_name()))

    for csv_score_item in csv_score_items:
        csv_score_item.set_is_predicate(predicate_info[csv_score_item.get_bug_key()])
        csv_score_item.set_is_crashing(crashing_info[csv_score_item.get_bug_key()])


if __name__ == '__main__':
    main()
