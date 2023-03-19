import copy
from typing import List

from entity_type import ScoredStatement


def assign_new_scores_to_list_statement(scored_statement_list: List[ScoredStatement]) -> List[ScoredStatement]:
    scored_statement_new_score_list = []
    last_score = 10
    index = 0
    while index < len(scored_statement_list):
        end_index = _get_tie_end_index(scored_statement_list, index)
        for tie_index in range(index, end_index + 1):
            new_scored_statement = copy.copy(scored_statement_list[tie_index])
            new_scored_statement.set_score(last_score)
            scored_statement_new_score_list.append(new_scored_statement)
        index = end_index + 1
        last_score = last_score / 2

    return scored_statement_new_score_list


def _get_tie_end_index(scored_statement_list: List[ScoredStatement], start_index: int) -> int:
    end_index = start_index
    start_index_score = scored_statement_list[start_index].get_score()
    for index in range(start_index, len(scored_statement_list)):
        if scored_statement_list[index].get_score() == start_index_score:
            end_index = index
        else:
            break
    return end_index
