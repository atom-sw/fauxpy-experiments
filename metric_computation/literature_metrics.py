import math
from typing import List, Dict

import mathematics
from entity_type import ScoredEntity, ScoredStatement, ScoredFunction


class EInspect:
    """
    Computes the E_Inspect of a given scored entity list.
    A scored entity list is a list of line numbers
    and their scores resulting from running a fault
    localization technique (e.g., Tarantula) on a buggy version.

    This class os based on paper "An Empirical Study of Fault Localization Families
    and Their Combinations". This ranking methods
    seems to be more reasonable that
    other methods (i.e., best case, worst case, and
     average case). So, we used this one.
    """

    def __init__(self, scored_entities: List[ScoredEntity],
                 line_counts: int,
                 bug_ground_truth: Dict):
        self._scored_entities = scored_entities
        self._line_counts = line_counts
        self._bug_ground_truth = bug_ground_truth

    @classmethod
    def _e_inspect(cls, p_start: float, t_tie_size: int, tf_faulty_count: int):
        """
        An implementation of E_Inspect based on the paper
        "An Empirical Study of Fault Localization Families and
        Their Combinations."

        :param p_start: location of the first tie element in the scored list.
        :param t_tie_size: number of tied elements.
        :param tf_faulty_count: number of faulty elements in the tie.
        :return: E_Inspect of the scored entities, which is a single value.
        """

        assert t_tie_size >= 2
        assert tf_faulty_count >= 1

        def num(k):
            return k * math.comb(t_tie_size - k - 1, tf_faulty_count - 1)

        den = math.comb(t_tie_size, tf_faulty_count)
        sigma_result = mathematics.math_sigma(num, 1, t_tie_size - tf_faulty_count)

        return p_start + sigma_result / den

    def get_e_inspect(self) -> float:
        bug_location_index = -1

        # Find the first bug location in scored entities.
        for index, scored_entity in enumerate(self._scored_entities):
            if self._is_bug_location(scored_entity):
                bug_location_index = index
                break

        # Fault localization technique found the bug.
        if bug_location_index != -1:
            bug_location_score = self._scored_entities[bug_location_index].get_score()
            start_index, end_index = self._get_tied_range(bug_location_score)

            # The first found bug location is not in a tie.
            if end_index - start_index == 0:
                assert bug_location_index == start_index == end_index
                e_inspect = float(bug_location_index + 1)
                return e_inspect

            # The first found bug location is in a tie.
            elif end_index - start_index > 0:
                assert start_index <= bug_location_index <= end_index
                num_faulty_in_tie = self._get_number_of_faulty_elements_in_tie(start_index, end_index)
                first_tie_item_rank = start_index + 1
                tie_size = end_index - start_index + 1
                e_inspect = self._e_inspect(first_tie_item_rank, tie_size, num_faulty_in_tie)
                return e_inspect

            else:
                raise Exception("This should never happen!")

        # Fault localization technique did not find the bug.
        else:
            num_faulty_in_tie = self._get_number_of_faulty_elements_in_ground_truth_info()
            first_tie_item_rank = len(self._scored_entities) + 1
            tie_size = self._line_counts - len(self._scored_entities)
            e_inspect = self._e_inspect(first_tie_item_rank, tie_size, num_faulty_in_tie)
            return e_inspect

    def _is_bug_location(self, scored_entity):
        if isinstance(scored_entity, ScoredStatement):
            lines_covered_entity = [scored_entity.get_line_number()]
        elif isinstance(scored_entity, ScoredFunction):
            function_range = scored_entity.get_function_range()
            lines_covered_entity = list(range(function_range[0], function_range[1] + 1))
        else:
            raise Exception("Should never happen!")

        scored_entity_ground_truth_line_numbers = self._get_scored_entity_ground_truth_line_numbers(
            scored_entity.get_file_path())
        for cov_line in lines_covered_entity:
            if cov_line in scored_entity_ground_truth_line_numbers:
                return True

        return False

    def _get_scored_entity_ground_truth_line_numbers(self, scored_entity_file_path) -> List[int]:
        scored_entity_ground_truth_file_path_list = list(
            filter(lambda x: x["FILE_NAME"] == scored_entity_file_path, self._bug_ground_truth))
        assert len(scored_entity_ground_truth_file_path_list) <= 1

        if len(scored_entity_ground_truth_file_path_list) > 0:
            scored_entity_ground_truth_file_path = scored_entity_ground_truth_file_path_list[0]
            lines = scored_entity_ground_truth_file_path["LINES"]
            extended_lines = scored_entity_ground_truth_file_path["EXTENDED_LINES"]

            return lines + extended_lines
        else:
            return []

    def _get_tied_range(self, bug_location_score):
        tied_index_list = []
        for index, item in enumerate(self._scored_entities):
            if item.get_score() == bug_location_score:
                tied_index_list.append(index)

        assert len(tied_index_list) != 0

        if len(tied_index_list) != 1:
            for index in range(1, len(tied_index_list)):
                assert tied_index_list[index] == tied_index_list[index - 1] + 1
            return tied_index_list[0], tied_index_list[-1]

        return tied_index_list[0], tied_index_list[0]

    def _get_number_of_faulty_elements_in_tie(self, start_index, end_index):
        num_faulty = 0
        for index in range(start_index, end_index + 1):
            if self._is_bug_location(self._scored_entities[index]):
                num_faulty += 1
        return num_faulty

    def _get_number_of_faulty_elements_in_ground_truth_info(self):
        number_of_faulty_elements_in_ground_truth_info = 0

        for item in self._bug_ground_truth:
            number_of_faulty_elements_in_ground_truth_info += len(item["LINES"]) + len(item["EXTENDED_LINES"])

        return number_of_faulty_elements_in_ground_truth_info
