import copy
from typing import List, Dict, Tuple

from tqdm import tqdm

import mathematics
from csv_score_load_manager import CsvScoreItem, FLGranularity


class MultiScoreStatement:
    def __init__(self,
                 statement_name: str,
                 score_dict: Dict[str, float],
                 is_faulty: bool):
        self._statement_name = statement_name
        self._score_dict = score_dict
        self._is_faulty = is_faulty

    def get_statement_name(self) -> str:
        return self._statement_name

    def get_scored_dict(self) -> Dict[str, float]:
        return copy.copy(self._score_dict)

    def get_is_fault_as_int(self) -> int:
        if self._is_faulty:
            return 1
        return 0


class ProjectBugItem:
    def __init__(self,
                 project_name: str,
                 bug_number: int,
                 line_count: int,
                 ground_truth_count: int,
                 qid: int,
                 project_counter: int,
                 multi_score_statement_list: List[MultiScoreStatement]):
        self._project_name = project_name
        self._bug_number = bug_number
        self._line_count = line_count
        self._ground_truth_count = ground_truth_count
        self._qid = qid
        self._project_counter = project_counter
        self._multi_score_statement_list = multi_score_statement_list

    def get_as_dict(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        key_item = self._get_project_counter_based_name()
        value_item = self._get_statements_dict()
        return {
            key_item: value_item
        }

    def get_qid(self) -> int:
        return self._qid

    def get_line_count(self) -> int:
        return self._line_count

    def get_ground_truth_count(self):
        return self._ground_truth_count

    def get_project_name(self) -> str:
        return self._project_name

    def get_bug_key(self) -> str:
        return f"{self._project_name}:{self._bug_number}"

    def get_output_length(self):
        return len(self._multi_score_statement_list)

    def _get_project_counter_based_name(self) -> str:
        return f"{self._project_name}{self._project_counter}"

    def _get_statements_dict(self) -> Dict[str, Dict[str, float]]:
        statements_dict = {}
        for multi_score_statement in self._multi_score_statement_list:
            current_statement_key = multi_score_statement.get_statement_name()
            current_statement_value = multi_score_statement.get_scored_dict()
            current_statement_value["faulty"] = multi_score_statement.get_is_fault_as_int()
            statements_dict[current_statement_key] = current_statement_value
        return statements_dict


class CombineFlManager:
    def __init__(self,
                 csv_score_items: List[CsvScoreItem],
                 ground_truth_info: Dict,
                 size_counts_info: Dict):
        assert any([x.get_granularity() == csv_score_items[0].get_granularity() for x in csv_score_items])
        self._csv_score_items = csv_score_items
        self._ground_truth_info = ground_truth_info
        self._size_counts_info = size_counts_info
        self._granularity = csv_score_items[0].get_granularity()
        self._bug_keys_sorted = self._get_sorted_bug_keys()
        self._qid = 1
        self._techniques_sorted, self._projects_sorted = self._get_sorted_techniques_and_projects()
        self._bug_technique_key_min_max_dict = self._get_bug_technique_key_min_max_dict()
        self._project_bug_item_sorted = self._get_sorted_project_bug_items()
        (self._qid_lines_csv_table,
         self._release_json_dict,
         self._qid_ground_truth_number_of_items) = self._get_qid_lines_csv_table_and_release_json_dict_and_ground_truth_num()

    def _get_qid_lines_csv_table_and_release_json_dict_and_ground_truth_num(self) -> Tuple[
        List[List[int]], Dict[str, Dict[str, Dict[str, float]]], Dict[int, int]]:
        qid_lines_table = []
        release_json_dict = {}
        ground_truth_count = {}
        for project_bug_item in self._project_bug_item_sorted:
            new_row = [project_bug_item.get_qid(), project_bug_item.get_line_count()]
            qid_lines_table.append(new_row)
            release_json_dict = release_json_dict | project_bug_item.get_as_dict()
            ground_truth_count[project_bug_item.get_qid()] = project_bug_item.get_ground_truth_count()
        return qid_lines_table, release_json_dict, ground_truth_count

    def get_release_json_dict_list(self) -> List[Dict[str, Dict[str, Dict[str, float]]]]:
        number_of_buggy_projects = len(self._release_json_dict.keys())
        number_of_files = 10
        number_of_bugs_in_each_file = int(number_of_buggy_projects / number_of_files) + 1

        release_json_dict_list = self._split_dictionary(self._release_json_dict, number_of_bugs_in_each_file)

        assert len(release_json_dict_list) == number_of_files

        all_keys = []
        for release_json_d in release_json_dict_list:
            for item_key in release_json_d.keys():
                all_keys.append(item_key)
        assert self._are_all_different_in_list(all_keys)

        assert len(all_keys) == number_of_buggy_projects

        return release_json_dict_list

    @staticmethod
    def _split_dictionary(input_dict: Dict[str, Dict[str, Dict[str, float]]],
                          chunk_size: int) -> List[Dict[str, Dict[str, Dict[str, float]]]]:
        """
        https://gist.github.com/nz-angel/31890d2c6cb1c9105e677cacc83a1ffd
        """

        res = []
        new_dict = {}
        for k, v in input_dict.items():
            if len(new_dict) < chunk_size:
                new_dict[k] = v
            else:
                res.append(new_dict)
                new_dict = {k: v}
        res.append(new_dict)
        return res

    def get_qid_lines_csv_table(self) -> List[List[int]]:
        return self._qid_lines_csv_table

    def get_qid_ground_truth_number_of_items_json_dict(self) -> Dict[int, int]:
        return self._qid_ground_truth_number_of_items

    def get_techniques_sorted_as_string(self) -> str:
        techniques_sorted_quoted = [f"\'{x}\'" for x in self._techniques_sorted]
        techniques_sorted_as_string = self._get_list_as_string(techniques_sorted_quoted)
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
        assert len(projects_list) == 13
        assert sum([x[1] for x in projects_list]) == 135

        return techniques_list, projects_list

    def _get_sorted_project_bug_items(self) -> List[ProjectBugItem]:
        project_bug_item_list = []
        previous_project_name = self._bug_keys_sorted[0].split(":")[0]
        project_counter = 0
        for bug_key in tqdm(self._bug_keys_sorted):
            current_bug_key_csv_score_item_list = [x for x in self._csv_score_items if x.get_bug_key() == bug_key]
            assert len(current_bug_key_csv_score_item_list) == len(self._techniques_sorted)
            current_project_name = current_bug_key_csv_score_item_list[0].get_project_name()
            if previous_project_name == current_project_name:
                project_counter += 1
            else:
                project_counter = 1
            previous_project_name = current_project_name
            current_project_bug_item = self._get_project_bug_item(current_bug_key_csv_score_item_list, project_counter)
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

    def _get_project_bug_item(self,
                              bug_key_csv_score_item_list: List[CsvScoreItem],
                              project_counter: int) -> ProjectBugItem:
        assert self._are_all_same_in_list([x.get_project_name() for x in bug_key_csv_score_item_list])
        assert self._are_all_same_in_list([x.get_bug_number() for x in bug_key_csv_score_item_list])
        assert bug_key_csv_score_item_list[0].get_granularity() == self._granularity
        assert self._are_all_same_in_list([x.get_granularity() for x in bug_key_csv_score_item_list])
        assert self._are_all_different_in_list([x.get_technique() for x in bug_key_csv_score_item_list])

        project_name = bug_key_csv_score_item_list[0].get_project_name()
        bug_number = bug_key_csv_score_item_list[0].get_bug_number()
        bug_key = bug_key_csv_score_item_list[0].get_bug_key()
        line_count = self._size_counts_info[bug_key_csv_score_item_list[0].get_bug_key()]
        ground_truth_count = self._get_number_of_ground_truth_items(bug_key)
        qid = self._qid
        self._qid += 1
        multi_score_statement_list = self._get_multi_score_statement_list(bug_key_csv_score_item_list)

        project_bug_it = ProjectBugItem(project_name,
                                        bug_number,
                                        line_count,
                                        ground_truth_count,
                                        qid,
                                        project_counter,
                                        multi_score_statement_list)
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
        assert len(bug_key_list) == 135

        return bug_key_list

    def _get_multi_score_statement_list(self,
                                        bug_key_csv_score_item_list: List[CsvScoreItem]) -> List[MultiScoreStatement]:
        all_statement_names_in_all_techniques = set()
        for csv_score_item in bug_key_csv_score_item_list:
            scored_statements = csv_score_item.get_scored_entities()
            # if len(scored_statements) > 0:
            # assert any([isinstance(x, ScoredStatement) for x in scored_statements])
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

    def _get_normalized_score_for_statement_name(self,
                                                 csv_score_item: CsvScoreItem,
                                                 statement_name: str) -> float:
        scored_statement_list_for_statement_name = [x for x in csv_score_item.get_scored_entities()
                                                    if x.get_entity_name() == statement_name]
        if len(scored_statement_list_for_statement_name) == 0:
            return 0

        assert len(scored_statement_list_for_statement_name) == 1

        current_score = scored_statement_list_for_statement_name[0].get_score()

        min_score, max_score = self._bug_technique_key_min_max_dict[csv_score_item.get_bug_technique_key()]

        current_score_normalized = mathematics.get_normalized_value(min_score, max_score, current_score)
        return current_score_normalized

    def _is_statement_faulty(self,
                             entity_name: str,
                             project_name: str,
                             bug_number: int) -> bool:
        entity_name_parts = entity_name.split("::")
        entity_module_name = entity_name_parts[0]
        if self._granularity == FLGranularity.Statement:
            entity_item = int(entity_name_parts[1])
        elif self._granularity == FLGranularity.Function:
            entity_item = "::".join(entity_name_parts[1:])
        elif self._granularity == FLGranularity.Module:
            entity_item = entity_name_parts[0]
        else:
            raise Exception()

        bug_key = self._get_bug_key(project_name, bug_number)
        current_bug_ground_truth_info = self._ground_truth_info[bug_key]
        for module_info_item in current_bug_ground_truth_info:
            if (entity_module_name == module_info_item["FILE_NAME"]
                    and entity_item in module_info_item["ITEMS"]):
                return True

        return False

    def _get_bug_technique_key_min_max_dict(self) -> Dict[str, Tuple[float, float]]:
        bug_technique_key_min_max_dict = {}
        for bug_key in self._bug_keys_sorted:
            bug_key_csv_score_item_list = [x for x in self._csv_score_items if x.get_bug_key() == bug_key]
            assert len(bug_key_csv_score_item_list) == 7
            assert self._are_all_same_in_list([x.get_project_name() for x in bug_key_csv_score_item_list])
            assert self._are_all_same_in_list([x.get_bug_number() for x in bug_key_csv_score_item_list])
            assert bug_key_csv_score_item_list[0].get_granularity() == self._granularity
            assert self._are_all_same_in_list([x.get_granularity() for x in bug_key_csv_score_item_list])
            assert self._are_all_different_in_list([x.get_technique() for x in bug_key_csv_score_item_list])
            for bug_key_csv in bug_key_csv_score_item_list:
                current_bug_technique_key = bug_key_csv.get_bug_technique_key()
                current_all_scores_in_csv = [x.get_score() for x in bug_key_csv.get_scored_entities()]
                if len(current_all_scores_in_csv) > 0:
                    min_score = min(current_all_scores_in_csv)
                    max_score = max(current_all_scores_in_csv)
                    bug_technique_key_min_max_dict[current_bug_technique_key] = (min_score, max_score)

        return bug_technique_key_min_max_dict

    def _get_number_of_ground_truth_items(self, bug_key) -> int:
        num_ground_truth_item = 0
        for module_item in self._ground_truth_info[bug_key]:
            current_module_count_item = len(module_item["ITEMS"])
            num_ground_truth_item += current_module_count_item

        return num_ground_truth_item

    def get_output_length(self) -> Dict[str, int]:
        output_length_dict = {}

        for item in self._project_bug_item_sorted:
            output_length_dict[item.get_bug_key()] = item.get_output_length()

        return output_length_dict
