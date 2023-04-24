from pathlib import Path
from typing import List

import file_manager
from csv_score_load_manager import CsvScoreItemLoadManager, FLTechnique, CsvScoreItem, ProjectType
from mutable_bug import MutableBugsAnalysis
from predicate_analysis import PredicateAnalysis


def main():
    path_manager = file_manager.PathManager()
    predicate_bug_info = file_manager.load_json_to_object(path_manager.get_predicate_bug_info_file_name())
    csv_score_item_load_manager = CsvScoreItemLoadManager(path_manager.get_results_path())
    statement_csv_score_items = csv_score_item_load_manager.load_csv_score_items()

    predicate_selected_bug_info = {}
    crashing_selected_bug_info = {}
    st_statement_csv_score_items = list(filter(lambda x: x.get_technique() == FLTechnique.ST,
                                               statement_csv_score_items))
    st_statement_csv_score_items.sort(key=lambda x: (x.get_project_name(), x.get_bug_number()))
    for statement_item in st_statement_csv_score_items:
        bug_key = statement_item.get_bug_key()
        if len(statement_item.get_scored_entities()) != 0:
            crashing_selected_bug_info[bug_key] = True
        else:
            crashing_selected_bug_info[bug_key] = False

        predicate_selected_bug_info[bug_key] = predicate_bug_info[bug_key]

    file_manager.save_object_to_json(crashing_selected_bug_info,
                                     Path(path_manager.get_crashing_selected_bug_info_file_name()))
    file_manager.save_object_to_json(predicate_selected_bug_info,
                                     Path(path_manager.get_predicate_selected_bug_info_file_name()))


def assign_type_to_selected_bugs(csv_score_items: List[CsvScoreItem],
                                 path_manager: file_manager.PathManager):
    dev_project_list = ["cookiecutter", "black", "luigi"]
    ds_project_list = ["spacy", "keras", "pandas"]
    web_project_list = ["sanic", "fastapi", "tornado"]
    cli_project_list = ["httpie", "thefuck", "tqdm", "youtube-dl"]

    crashing_info = (file_manager.
                     load_json_to_object(path_manager.
                                         get_crashing_selected_bug_info_file_name()))
    predicate_info = (file_manager.
                      load_json_to_object(path_manager.
                                          get_predicate_selected_bug_info_file_name()))

    ground_truth_info = file_manager.load_json_to_object(path_manager.get_ground_truth_file_name())
    mutation_analysis = MutableBugsAnalysis(path_manager.get_results_path(), ground_truth_info)
    mutable_bug_key_list = mutation_analysis.get_mutable_bug_keys()
    percentage_dict = mutation_analysis.get_percentage_of_mutants_on_ground_truth()

    predicate_analysis = PredicateAnalysis(path_manager.get_results_path())
    number_of_predicate_instances_dict = predicate_analysis.get_number_of_predicate_instances_dict()

    for csv_score_item in csv_score_items:
        csv_score_item.set_is_predicate(predicate_info[csv_score_item.get_bug_key()])
        csv_score_item.set_is_crashing(crashing_info[csv_score_item.get_bug_key()])
        csv_score_item.set_is_mutable_bug(csv_score_item.get_bug_key() in mutable_bug_key_list)
        csv_score_item.set_percentage_of_mutants_on_ground_truth(percentage_dict[csv_score_item.get_bug_key()])

        if csv_score_item.get_project_name() in dev_project_list:
            csv_score_item.set_project_type(ProjectType.Dev)
        elif csv_score_item.get_project_name() in ds_project_list:
            csv_score_item.set_project_type(ProjectType.DS)
        elif csv_score_item.get_project_name() in web_project_list:
            csv_score_item.set_project_type(ProjectType.Web)
        elif csv_score_item.get_project_name() in cli_project_list:
            csv_score_item.set_project_type(ProjectType.CLI)
        else:
            print(csv_score_item.get_project_name())
            raise Exception()

        if csv_score_item.get_technique() == FLTechnique.PS:
            (current_number_of_predicate_instances,
             current_number_of_failing_tests) = number_of_predicate_instances_dict[csv_score_item.get_bug_key()]
            assert current_number_of_predicate_instances >= current_number_of_failing_tests
            csv_score_item.set_number_of_predicate_instances(current_number_of_predicate_instances)
            csv_score_item.set_number_of_failing_tests(current_number_of_failing_tests)


if __name__ == '__main__':
    main()
