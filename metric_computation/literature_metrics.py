import math
from typing import List, Tuple

import mathematics
from entity_type import ScoredEntity


class EInspectBase:
    def __init__(self,
                 scored_entities: List[ScoredEntity],
                 buggy_entity_names: List[str]):
        self._scored_entities = scored_entities
        self._buggy_entity_names = buggy_entity_names

    @classmethod
    def e_inspect(cls, p_start: float, t_tie_size: int, tf_faulty_count: int):
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

    def is_bug_location(self, scored_entity: ScoredEntity) -> bool:
        return scored_entity.get_entity_name() in self._buggy_entity_names

    def get_tied_range(self, bug_location_score: float) -> Tuple[int, int]:
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

    def get_number_of_faulty_elements_in_tie(self, start_index, end_index):
        num_faulty = 0
        for index in range(start_index, end_index + 1):
            if self.is_bug_location(self._scored_entities[index]):
                num_faulty += 1
        return num_faulty


class EInspect(EInspectBase):
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

    def __init__(self, scored_entities: List[ScoredEntity], entity_count_in_project: int,
                 buggy_entity_names: List[str]):
        super().__init__(scored_entities, buggy_entity_names)
        self._entity_count_in_project = entity_count_in_project
        self._is_bug_localized = False

    def is_bug_localized(self) -> bool:
        return self._is_bug_localized

    def get_e_inspect(self) -> float:
        bug_location_index = -1

        # Find the first bug location in scored entities.
        for index, scored_entity in enumerate(self._scored_entities):
            if self.is_bug_location(scored_entity):
                bug_location_index = index
                break

        # Fault localization technique found the bug.
        if bug_location_index != -1:
            self._is_bug_localized = True
            bug_location_score = self._scored_entities[bug_location_index].get_score()
            start_index, end_index = self.get_tied_range(bug_location_score)

            # The first found bug location is not in a tie.
            if end_index - start_index == 0:
                assert bug_location_index == start_index == end_index
                e_inspect = float(bug_location_index + 1)
                return e_inspect

            # The first found bug location is in a tie.
            elif end_index - start_index > 0:
                assert start_index <= bug_location_index <= end_index
                num_faulty_in_tie = self.get_number_of_faulty_elements_in_tie(start_index, end_index)
                first_tie_item_rank = start_index + 1
                tie_size = end_index - start_index + 1
                e_inspect = self.e_inspect(first_tie_item_rank, tie_size, num_faulty_in_tie)
                return e_inspect

            else:
                raise Exception("This should never happen!")

        # Fault localization technique did not find the bug.
        else:
            self._is_bug_localized = False
            first_tie_item_rank = len(self._scored_entities) + 1
            tie_size = self._entity_count_in_project - len(self._scored_entities)
            e_inspect = self.e_inspect(first_tie_item_rank, tie_size, len(self._buggy_entity_names))
            return e_inspect
