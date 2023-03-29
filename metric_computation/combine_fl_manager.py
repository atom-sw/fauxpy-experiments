from typing import List, Dict, Tuple

import mathematics
from csv_score_load_manager import CsvScoreItem, FLGranularity
from entity_type import ScoredStatement


class MultiScoreStatement:
    def __init__(self,
                 statement_name: str,
                 score_dict: Dict[str, float],
                 is_faulty: bool):
        self._statement_name = statement_name
        self._score_dict = score_dict
        self._is_faulty = is_faulty


class ProjectBugItem:
    def __init__(self,
                 project_name: str,
                 bug_number: int,
                 line_count: int,
                 qid: int,
                 multi_score_statement_list: List[MultiScoreStatement]):
        self._project_name = project_name
        self._bug_number = bug_number
        self._line_count = line_count
        self._qid = qid
        self._multi_score_statement_list = multi_score_statement_list


class CombineFlManager:
    def __init__(self,
                 fauxpy_statement_csv_score_items: List[CsvScoreItem],
                 ground_truth_info: Dict,
                 size_counts_info: Dict):
        self._csv_score_items = fauxpy_statement_csv_score_items
        self._ground_truth_info = ground_truth_info
        self._size_counts_info = size_counts_info
        self._bug_keys_sorted = self._get_sorted_bug_keys()
        self._qid = 1
        self._techniques_sorted, self._projects_sorted = self._get_sorted_techniques_and_projects()
        self._project_bug_item_sorted = self._get_sorted_project_bug_items()

    def get_release_json_dict(self):
        pass

    def get_qid_lines_csv_table(self):
        pass

    def get_techniques_sorted_as_string(self) -> str:
        techniques_sorted_as_string = self._get_list_as_string(self._techniques_sorted)
        return techniques_sorted_as_string

    def get_projects_sorted_as_string(self) -> str:
        projects_sorted_as_string = self._get_list_as_string(self._projects_sorted)
        return projects_sorted_as_string

    def _get_sorted_techniques_and_projects(self) -> Tuple[List[str], List[Tuple[str, int]]]:
        technique_set = set()
        projects_dict = {}

        bug_key_0_csv_score_item_list = [x for x in self._csv_score_items if
                                         x.get_bug_key() == self._bug_keys_sorted[0]]
        assert len(bug_key_0_csv_score_item_list) == 7
        for bug_key_csv_score_item in bug_key_0_csv_score_item_list:
            technique_set.add(bug_key_csv_score_item.get_technique())

        for bug_key in self._bug_keys_sorted:
            bug_key_csv_score_item_technique_0 = [x for x in self._csv_score_items if x.get_bug_key() == bug_key][0]
            current_project_nam = bug_key_csv_score_item_technique_0.get_project_name()
            if current_project_nam in projects_dict.keys():
                projects_dict[current_project_nam] += 1
            else:
                projects_dict[current_project_nam] = 1

        techniques_list = [x.name for x in technique_set]
        techniques_list.sort()
        assert len(techniques_list) == 7

        projects_list = [(x[0], x[1]) for x in projects_dict.items()]
        assert len(projects_list) == 12
        assert sum([x[1] for x in projects_list]) == 121

        return techniques_list, projects_list

    def _get_sorted_project_bug_items(self) -> List[ProjectBugItem]:
        project_bug_item_list = []
        for bug_key in self._bug_keys_sorted:
            current_bug_key_csv_score_item_list = [x for x in self._csv_score_items if x.get_bug_key() == bug_key]
            assert len(current_bug_key_csv_score_item_list) == len(self._techniques_sorted)
            current_project_bug_item = self._get_project_bug_item(current_bug_key_csv_score_item_list)
            project_bug_item_list.append(current_project_bug_item)

        return project_bug_item_list

    @staticmethod
    def _get_list_as_string(item_list: List) -> str:
        list_as_string = "[\n"
        for item in item_list:
            list_as_string += f"{item},\n"
        list_as_string = list_as_string[:-2]
        list_as_string += "\n]"
        return list_as_string

    @staticmethod
    def _get_bug_key(project_name: str, bug_number: int) -> str:
        return f"{project_name}:{bug_number}"

    def _get_project_bug_item(self, bug_key_csv_score_item_list: List[CsvScoreItem]) -> ProjectBugItem:
        assert self._are_all_same_in_list([x.get_project_name() for x in bug_key_csv_score_item_list])
        assert self._are_all_same_in_list([x.get_bug_number() for x in bug_key_csv_score_item_list])
        assert bug_key_csv_score_item_list[0].get_granularity() == FLGranularity.Statement
        assert self._are_all_same_in_list([x.get_granularity() for x in bug_key_csv_score_item_list])
        assert self._are_all_different_in_list([x.get_technique() for x in bug_key_csv_score_item_list])

        project_name = bug_key_csv_score_item_list[0].get_project_name()
        bug_number = bug_key_csv_score_item_list[0].get_bug_number()
        line_count = self._size_counts_info[bug_key_csv_score_item_list[0].get_bug_key()]["LINE_COUNT"]
        qid = self._qid
        self._qid += 1
        multi_score_statement_list = self._get_multi_score_statement_list(bug_key_csv_score_item_list)

        project_bug_it = ProjectBugItem(project_name, bug_number, line_count, qid, multi_score_statement_list)
        return project_bug_it

    @staticmethod
    def _are_all_same_in_list(item_list: List) -> bool:
        if len(item_list) == 0:
            return False

        first_element = item_list[0]
        for item in item_list:
            if item != first_element:
                return False

        return True

    @staticmethod
    def _are_all_different_in_list(item_list) -> bool:
        if len(item_list) == 0:
            return False

        for index_1 in range(0, len(item_list)):
            for index_2 in range(index_1 + 1, len(item_list)):
                if item_list[index_1] == item_list[index_2]:
                    return False

        return True

    def _get_sorted_bug_keys(self) -> List[str]:
        bug_keys_dict = {}

        for csv_score_item in self._csv_score_items:
            current_project_nam = csv_score_item.get_project_name()
            current_bug_number = csv_score_item.get_bug_number()
            current_bug_key = csv_score_item.get_bug_key()
            if current_bug_key not in bug_keys_dict.keys():
                bug_keys_dict[current_bug_key] = (current_project_nam, current_bug_number)

        bug_key_values_list = list(bug_keys_dict.values())
        bug_key_values_list.sort(key=lambda x: (x[0], x[1]))

        bug_key_list = [self._get_bug_key(x[0], x[1]) for x in bug_key_values_list]
        assert len(bug_key_list) == 121

        return bug_key_list

    def _get_multi_score_statement_list(self,
                                        bug_key_csv_score_item_list: List[CsvScoreItem]) -> List[MultiScoreStatement]:
        all_statement_names_in_all_techniques = set()
        for csv_score_item in bug_key_csv_score_item_list:
            scored_statements = csv_score_item.get_scored_entities()
            if len(scored_statements) > 0:
                assert any([isinstance(x, ScoredStatement) for x in scored_statements])
            for item in scored_statements:
                all_statement_names_in_all_techniques.add(item.get_entity_name())

        multi_score_statement_list = []
        project_name = bug_key_csv_score_item_list[0].get_project_name()
        bug_number = bug_key_csv_score_item_list[0].get_bug_number()
        for statement_name in all_statement_names_in_all_techniques:
            scored_dict = self._get_scored_dict_for_statement_name(statement_name, bug_key_csv_score_item_list)
            is_statement_faulty = self._is_statement_faulty(statement_name, project_name, bug_number)
            current_multi_score_statement = MultiScoreStatement(statement_name, scored_dict, is_statement_faulty)
            multi_score_statement_list.append(current_multi_score_statement)

        return multi_score_statement_list

    def _get_scored_dict_for_statement_name(self,
                                            statement_name: str,
                                            bug_key_csv_score_item_list: List[CsvScoreItem]) -> Dict:
        scored_list = []
        for csv_score_item in bug_key_csv_score_item_list:
            current_technique = csv_score_item.get_technique()
            current_score = self._get_normalized_score_for_statement_name(csv_score_item, statement_name)
            scored_list.append((current_technique, current_score))

        scored_list.sort(key=lambda x: x[0].name)

        scored_dict = {}
        for item in scored_list:
            scored_dict[item[0].name] = item[1]

        return scored_dict

    @staticmethod
    def _get_normalized_score_for_statement_name(csv_score_item: CsvScoreItem,
                                                 statement_name: str) -> float:
        scored_statement_list_for_statement_name = [x for x in csv_score_item.get_scored_entities()
                                                    if x.get_entity_name() == statement_name]
        if len(scored_statement_list_for_statement_name) == 0:
            return 0

        assert len(scored_statement_list_for_statement_name) == 1

        current_score = scored_statement_list_for_statement_name[0].get_score()

        all_scores_in_csv_score_item = [x.get_score() for x in csv_score_item.get_scored_entities()]
        min_score = min(all_scores_in_csv_score_item)
        max_score = max(all_scores_in_csv_score_item)

        current_score_normalized = mathematics.get_normalized_value(min_score, max_score, current_score)
        return current_score_normalized

    def _is_statement_faulty(self,
                             statement_name: str,
                             project_name: str,
                             bug_number: int):
        statement_name_parts = statement_name.split("::")
        statement_module_name = statement_name_parts[0]
        statement_line_number = int(statement_name_parts[1])
        bug_key = self._get_bug_key(project_name, bug_number)
        current_bug_ground_truth_info = self._ground_truth_info[bug_key]
        for module_info_item in current_bug_ground_truth_info:
            if (statement_module_name == module_info_item["FILE_NAME"]
                    and statement_line_number in
                    (module_info_item["LINES"] + module_info_item["EXTENDED_LINES"])):
                return True

        return False
