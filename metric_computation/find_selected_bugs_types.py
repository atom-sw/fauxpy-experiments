from pathlib import Path

import file_manager
from csv_score_load_manager import CsvScoreItemLoadManager, FLTechnique


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


if __name__ == '__main__':
    main()
